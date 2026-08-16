#!/usr/bin/env python3
"""Select and execute the minimal sufficient validation set for a change."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import sys
import time
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPOSITORY_ROOT / "validation/profiles.toml"
FULL_EVENTS = frozenset({"push", "workflow_dispatch"})


class RoutingError(RuntimeError):
    """Report an invalid routing definition or invocation."""


@dataclass(frozen=True)
class Profile:
    """A repository responsibility and its authoritative check command."""

    identifier: str
    description: str
    command: tuple[str, ...]
    paths: tuple[str, ...]


@dataclass(frozen=True)
class RoutingConfig:
    """Validated canonical routing configuration."""

    version: int
    full_events: frozenset[str]
    fallback_profiles: tuple[str, ...]
    routing_owner_paths: tuple[str, ...]
    profiles: tuple[Profile, ...]

    @property
    def profile_ids(self) -> tuple[str, ...]:
        """Return profile identifiers in deterministic execution order."""

        return tuple(profile.identifier for profile in self.profiles)


def _string_list(raw: Any, field: str) -> tuple[str, ...]:
    if not isinstance(raw, list) or not raw or not all(isinstance(item, str) and item for item in raw):
        raise RoutingError(f"{field} must be a non-empty string array")
    return tuple(raw)


def load_config(path: Path = DEFAULT_CONFIG) -> RoutingConfig:
    """Load and validate the sole routing source of truth."""

    with path.open("rb") as stream:
        raw = tomllib.load(stream)

    version = raw.get("version")
    if version != 1:
        raise RoutingError(f"unsupported routing schema version: {version!r}")

    raw_profiles = raw.get("profiles")
    if not isinstance(raw_profiles, list) or not raw_profiles:
        raise RoutingError("profiles must be a non-empty array")

    profiles: list[Profile] = []
    identifiers: set[str] = set()
    for index, payload in enumerate(raw_profiles):
        if not isinstance(payload, dict):
            raise RoutingError(f"profiles[{index}] must be a table")
        identifier = payload.get("id")
        description = payload.get("description")
        if not isinstance(identifier, str) or not identifier:
            raise RoutingError(f"profiles[{index}].id must be a non-empty string")
        if identifier in identifiers:
            raise RoutingError(f"duplicate profile id: {identifier}")
        if not isinstance(description, str) or not description:
            raise RoutingError(f"profiles[{index}].description must be a non-empty string")
        profiles.append(
            Profile(
                identifier=identifier,
                description=description,
                command=_string_list(payload.get("command"), f"profiles[{index}].command"),
                paths=_string_list(payload.get("paths"), f"profiles[{index}].paths"),
            )
        )
        identifiers.add(identifier)

    full_events = frozenset(_string_list(raw.get("full_events"), "full_events"))
    if not FULL_EVENTS.issubset(full_events):
        missing = sorted(FULL_EVENTS - full_events)
        raise RoutingError(f"full_events must include integration events: {missing}")

    fallback_profiles = _string_list(raw.get("fallback_profiles"), "fallback_profiles")
    unknown_fallbacks = sorted(set(fallback_profiles) - identifiers)
    if unknown_fallbacks:
        raise RoutingError(f"unknown fallback profiles: {unknown_fallbacks}")

    return RoutingConfig(
        version=version,
        full_events=full_events,
        fallback_profiles=fallback_profiles,
        routing_owner_paths=_string_list(raw.get("routing_owner_paths"), "routing_owner_paths"),
        profiles=tuple(profiles),
    )


def normalize_path(path: str) -> str:
    """Normalize a repository-relative path and reject traversal."""

    candidate = PurePosixPath(path.replace("\\", "/"))
    normalized = candidate.as_posix().removeprefix("./")
    if (
        candidate.is_absolute()
        or normalized in {"", "."}
        or any(part in {"", ".", ".."} for part in candidate.parts)
    ):
        raise RoutingError(f"invalid repository-relative path: {path!r}")
    return normalized


def path_matches(path: str, pattern: str) -> bool:
    """Match root files and recursive paths with predictable glob semantics."""

    normalized_path = normalize_path(path)
    normalized_pattern = pattern.replace("\\", "/").removeprefix("./")
    if fnmatch.fnmatchcase(normalized_path, normalized_pattern):
        return True
    if normalized_pattern.startswith("**/"):
        return fnmatch.fnmatchcase(normalized_path, normalized_pattern[3:])
    return False


def classify_paths(config: RoutingConfig, paths: Sequence[str], event: str) -> dict[str, Any]:
    """Project changed paths onto responsibility profiles."""

    normalized_paths = tuple(sorted({normalize_path(path) for path in paths}))
    full_mode = event in config.full_events
    owner_paths = tuple(
        path
        for path in normalized_paths
        if any(path_matches(path, pattern) for pattern in config.routing_owner_paths)
    )
    self_change = bool(owner_paths)

    matched_by_profile: dict[str, list[str]] = {
        profile.identifier: [] for profile in config.profiles
    }
    classified_paths: set[str] = set()
    if not full_mode and not self_change:
        for profile in config.profiles:
            for path in normalized_paths:
                if any(path_matches(path, pattern) for pattern in profile.paths):
                    matched_by_profile[profile.identifier].append(path)
                    classified_paths.add(path)

    unclassified_paths = tuple(path for path in normalized_paths if path not in classified_paths)
    if not full_mode and not self_change and unclassified_paths:
        for identifier in config.fallback_profiles:
            matched_by_profile[identifier].extend(unclassified_paths)

    profile_payloads: list[dict[str, Any]] = []
    for profile in config.profiles:
        matched = tuple(sorted(set(matched_by_profile[profile.identifier])))
        applicable = full_mode or self_change or bool(matched)
        if full_mode:
            reason = f"full integration event: {event}"
        elif self_change:
            reason = "routing authority changed; conservative self-validation"
        elif matched:
            reason = "matched changed responsibility"
        else:
            reason = "independent responsibility not changed"
        profile_payloads.append(
            {
                "id": profile.identifier,
                "description": profile.description,
                "command": list(profile.command),
                "state": "applicable" if applicable else "not_applicable",
                "matched_paths": list(matched),
                "reason": reason,
            }
        )

    return {
        "schema_version": 1,
        "event": event,
        "mode": "full" if full_mode else "changed-responsibility",
        "changed_paths": list(normalized_paths),
        "routing_owner_paths": list(owner_paths),
        "self_change": self_change,
        "unclassified_paths": list(unclassified_paths),
        "profiles": profile_payloads,
    }


def changed_paths_from_git(root: Path, base: str, head: str) -> list[str]:
    """Read the committed change set without depending on GitHub-specific actions."""

    if not base or not head:
        raise RoutingError("base and head are required for pull_request routing")
    result = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only", "--diff-filter=ACMRDT", f"{base}...{head}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RoutingError(f"git diff failed: {result.stderr.strip()}")
    return [line for line in result.stdout.splitlines() if line]


def resolve_paths(args: argparse.Namespace, config: RoutingConfig) -> list[str]:
    """Resolve explicit fixture paths or the actual Git diff."""

    explicit = list(args.changed_file or [])
    if args.changed_files_file:
        explicit.extend(
            line.strip()
            for line in Path(args.changed_files_file).read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    if explicit:
        return explicit
    if args.event in config.full_events:
        return []
    return changed_paths_from_git(args.root, args.base, args.head)


def profile_states(plan: Mapping[str, Any]) -> dict[str, str]:
    """Extract validated profile applicability from a plan."""

    profiles = plan.get("profiles")
    if not isinstance(profiles, list):
        raise RoutingError("plan profiles must be an array")
    states: dict[str, str] = {}
    for profile in profiles:
        if not isinstance(profile, dict):
            raise RoutingError("plan profile must be an object")
        identifier = profile.get("id")
        state = profile.get("state")
        if not isinstance(identifier, str) or state not in {"applicable", "not_applicable"}:
            raise RoutingError("invalid profile id or state in plan")
        states[identifier] = state
    return states


def aggregate_outcomes(plan: Mapping[str, Any], outcomes: Mapping[str, str]) -> dict[str, str]:
    """Map execution outcomes to final states while ignoring non-applicable failures."""

    final: dict[str, str] = {}
    for identifier, state in profile_states(plan).items():
        if state == "not_applicable":
            final[identifier] = "not_applicable"
            continue
        outcome = outcomes.get(identifier, "not_run")
        if outcome not in {"pass", "fail", "not_run"}:
            raise RoutingError(f"invalid outcome for {identifier}: {outcome}")
        final[identifier] = outcome
    return final


def execute_plan(plan: Mapping[str, Any], root: Path) -> tuple[dict[str, Any], int]:
    """Execute only applicable profile commands and retain complete evidence."""

    profiles = plan.get("profiles")
    if not isinstance(profiles, list):
        raise RoutingError("plan profiles must be an array")

    environment = os.environ.copy()
    source_paths = os.pathsep.join((str(root / "python"), str(root)))
    existing_pythonpath = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = (
        source_paths if not existing_pythonpath else os.pathsep.join((source_paths, existing_pythonpath))
    )
    environment["PROJECT_TEMPLATE_IMAGE"] = "1"

    evidence: list[dict[str, Any]] = []
    exit_code = 0
    for profile in profiles:
        if not isinstance(profile, dict):
            raise RoutingError("plan profile must be an object")
        identifier = profile.get("id")
        state = profile.get("state")
        command = profile.get("command")
        if not isinstance(identifier, str) or state not in {"applicable", "not_applicable"}:
            raise RoutingError("invalid profile in plan")
        if not isinstance(command, list) or not command or not all(isinstance(item, str) for item in command):
            raise RoutingError(f"invalid command for {identifier}")
        if state == "not_applicable":
            evidence.append(
                {
                    "id": identifier,
                    "applicability": "not_applicable",
                    "result": "not_applicable",
                    "command": command,
                    "returncode": None,
                    "duration_seconds": 0.0,
                }
            )
            continue

        print(f"VALIDATION_PROFILE_START={identifier}", flush=True)
        started = time.monotonic()
        completed = subprocess.run(command, cwd=root, env=environment, check=False)
        duration = round(time.monotonic() - started, 3)
        result = "pass" if completed.returncode == 0 else "fail"
        print(
            f"VALIDATION_PROFILE_RESULT={identifier}:{result}:returncode={completed.returncode}:duration={duration}",
            flush=True,
        )
        evidence.append(
            {
                "id": identifier,
                "applicability": "applicable",
                "result": result,
                "command": command,
                "returncode": completed.returncode,
                "duration_seconds": duration,
            }
        )
        if completed.returncode != 0:
            exit_code = 1

    result_payload = {
        "schema_version": 1,
        "event": plan.get("event"),
        "mode": plan.get("mode"),
        "changed_paths": plan.get("changed_paths", []),
        "profiles": evidence,
        "result": "pass" if exit_code == 0 else "fail",
    }
    return result_payload, exit_code


def render_plan_summary(plan: Mapping[str, Any]) -> str:
    """Render applicability evidence for humans without conflating N/A and pass."""

    lines = [
        "## Validation routing plan",
        "",
        f"- Event: `{plan.get('event')}`",
        f"- Mode: `{plan.get('mode')}`",
        f"- Routing self-change: `{str(bool(plan.get('self_change'))).lower()}`",
        "",
        "| Profile | State | Reason |",
        "| --- | --- | --- |",
    ]
    profiles = plan.get("profiles", [])
    if isinstance(profiles, list):
        for profile in profiles:
            if isinstance(profile, dict):
                lines.append(
                    f"| `{profile.get('id')}` | `{profile.get('state')}` | {profile.get('reason')} |"
                )
    changed_paths = plan.get("changed_paths", [])
    if isinstance(changed_paths, list):
        lines.extend(("", "Changed paths:", ""))
        if changed_paths:
            lines.extend(f"- `{path}`" for path in changed_paths)
        else:
            lines.append("- Integration event; path classification is not used.")
    return "\n".join(lines) + "\n"


def render_result_summary(result: Mapping[str, Any]) -> str:
    """Render execution evidence with explicit non-applicable states."""

    lines = [
        "## Validation results",
        "",
        f"Overall: **{result.get('result')}**",
        "",
        "| Profile | Applicability | Result | Duration (s) |",
        "| --- | --- | --- | ---: |",
    ]
    profiles = result.get("profiles", [])
    if isinstance(profiles, list):
        for profile in profiles:
            if isinstance(profile, dict):
                lines.append(
                    "| `{}` | `{}` | `{}` | {} |".format(
                        profile.get("id"),
                        profile.get("applicability"),
                        profile.get("result"),
                        profile.get("duration_seconds"),
                    )
                )
    return "\n".join(lines) + "\n"


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Write deterministic machine-readable evidence."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_summary(path: Path, text: str) -> None:
    """Append Markdown evidence to a summary artifact."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(text)


def write_github_outputs(path: Path, plan: Mapping[str, Any], plan_file: Path) -> None:
    """Expose only projections of the canonical plan to the workflow."""

    states = profile_states(plan)
    with path.open("a", encoding="utf-8") as stream:
        stream.write(f"plan_file={plan_file.as_posix()}\n")
        for identifier, state in sorted(states.items()):
            key = identifier.replace("-", "_") + "_applicable"
            stream.write(f"{key}={'true' if state == 'applicable' else 'false'}\n")


def add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT)
    parser.add_argument("--event", default="pull_request")
    parser.add_argument("--base", default="")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--changed-file", action="append", default=[])
    parser.add_argument("--changed-files-file", type=Path)


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    config = load_config(args.config)
    return classify_paths(config, resolve_paths(args, config), args.event)


def command_plan(args: argparse.Namespace) -> int:
    plan = build_plan(args)
    write_json(args.plan_file, plan)
    if args.summary_file:
        append_summary(args.summary_file, render_plan_summary(plan))
    if args.github_output:
        write_github_outputs(args.github_output, plan, args.plan_file)
    print(f"VALIDATION_PLAN={json.dumps(plan, sort_keys=True, separators=(',', ':'))}")
    return 0


def command_run(args: argparse.Namespace) -> int:
    if args.plan_file is not None:
        if not args.plan_file.is_file():
            raise RoutingError(f"plan file does not exist: {args.plan_file}")
        plan = json.loads(args.plan_file.read_text(encoding="utf-8"))
    else:
        plan = build_plan(args)
        if args.write_plan_file is not None:
            write_json(args.write_plan_file, plan)
    result, exit_code = execute_plan(plan, args.root.resolve())
    write_json(args.result_file, result)
    if args.summary_file:
        append_summary(args.summary_file, render_result_summary(result))
    print(f"VALIDATION_RESULT={json.dumps(result, sort_keys=True, separators=(',', ':'))}")
    return exit_code


def command_describe(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    print("profile\tcommand\tresponsibility")
    for profile in config.profiles:
        print(f"{profile.identifier}\t{' '.join(profile.command)}\t{profile.description}")
    return 0


def parser() -> argparse.ArgumentParser:
    root_parser = argparse.ArgumentParser(description=__doc__)
    subparsers = root_parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="classify changed responsibilities")
    add_common_arguments(plan_parser)
    plan_parser.add_argument("--plan-file", type=Path, default=Path(".state/validation-plan.json"))
    plan_parser.add_argument("--summary-file", type=Path)
    plan_parser.add_argument("--github-output", type=Path)
    plan_parser.set_defaults(handler=command_plan)

    run_parser = subparsers.add_parser("run", help="execute applicable profile checks")
    add_common_arguments(run_parser)
    run_parser.add_argument("--plan-file", type=Path)
    run_parser.add_argument("--write-plan-file", type=Path)
    run_parser.add_argument("--result-file", type=Path, default=Path(".state/validation-result.json"))
    run_parser.add_argument("--summary-file", type=Path)
    run_parser.set_defaults(handler=command_run)

    describe_parser = subparsers.add_parser("describe", help="print the canonical check matrix")
    describe_parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    describe_parser.set_defaults(handler=command_describe)
    return root_parser


def main() -> int:
    args = parser().parse_args()
    try:
        return int(args.handler(args))
    except (OSError, RoutingError, json.JSONDecodeError, tomllib.TOMLDecodeError) as error:
        print(f"VALIDATION_ROUTING_ERROR={error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
