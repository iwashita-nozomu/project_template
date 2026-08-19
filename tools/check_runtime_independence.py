#!/usr/bin/env python3
"""Validate that the template and its normal execution paths are self-contained."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Entry:
    mode: str
    object_id: str
    path: str


AGENT_CANON_PATH = "vendor/agent-canon"
AGENT_CANON_SUBMODULE_CONFIG = {
    "submodule.vendor/agent-canon.path": AGENT_CANON_PATH,
    "submodule.vendor/agent-canon.url": "https://github.com/iwashita-nozomu/agent-canon.git",
    "submodule.vendor/agent-canon.branch": "main",
}

FORBIDDEN_TRACKED_PATHS = {
    ".agent-canon/update-state.toml",
    ".github/scripts/checkout_agent_canon_submodule.sh",
    ".github/workflows/agent-coordination.yml",
    ".github/workflows/agent-improvement-guide.yml",
    "tools/agent-canon",
}

EXECUTION_PATHS = (
    "Makefile",
    "pyproject.toml",
    "scripts/",
    "docker/",
    ".devcontainer/",
    ".github/workflows/",
    ".github/scripts/",
    ".vscode/",
)

FORBIDDEN_RUNTIME_TEXT = (
    "vendor/agent-canon",
    "tools/agent-canon",
    "AGENT_CANON_READ_TOKEN",
    "AGENT_CANON_REPO_TOKEN",
    "AGENT_CANON_REPO_SSH_KEY",
    "AGENT_CANON_TEMPLATE_SUBMODULE_STRATEGY",
    "submodule_strategy",
    "agent-canon-update",
    "agent-canon-latest-check",
    "agent_canon_source_root",
    "checkout_agent_canon_submodule",
    "PYTHONPATH=vendor/agent-canon",
    ".agent-canon/docker-compose.generated.yml",
)

SCAN_EXCLUSIONS = {
    "tools/check_runtime_independence.py",
    "docker/check_zero_build_contract.sh",
}


def fail(message: str) -> None:
    print(f"RUNTIME_INDEPENDENCE_FINDING={message}", file=sys.stderr)
    raise SystemExit(1)


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"git-command-failed:{' '.join(args)}:{result.stderr.strip()}")
    return result.stdout


def tracked_entries(root: Path) -> list[Entry]:
    output = git(root, "ls-files", "-s", "-z")
    entries: list[Entry] = []
    for record in output.split("\0"):
        if not record:
            continue
        metadata, path = record.split("\t", 1)
        mode, object_id, _stage = metadata.split()
        entries.append(Entry(mode=mode, object_id=object_id, path=path))
    return entries


def is_execution_path(path: str) -> bool:
    return any(path == prefix or path.startswith(prefix) for prefix in EXECUTION_PATHS)


def submodule_config(root: Path) -> dict[str, str]:
    result = subprocess.run(
        [
            "git",
            "config",
            "--file",
            str(root / ".gitmodules"),
            "--get-regexp",
            r"^submodule\.",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"agent-canon-submodule-config-unreadable:{result.stderr.strip()}")

    parsed: dict[str, str] = {}
    for line in result.stdout.splitlines():
        key, separator, value = line.partition(" ")
        if not separator or key in parsed:
            fail(f"agent-canon-submodule-config-invalid:{line}")
        parsed[key] = value
    return parsed


def validate_agent_canon_registration(root: Path, entries: list[Entry]) -> None:
    by_path = {entry.path: entry for entry in entries}
    metadata = by_path.get(".gitmodules")
    if metadata is None:
        fail("agent-canon-submodule-metadata-missing")
    if metadata.mode != "100644":
        fail(f"agent-canon-submodule-metadata-not-regular:{metadata.mode}")

    config = submodule_config(root)
    if config != AGENT_CANON_SUBMODULE_CONFIG:
        fail(f"agent-canon-submodule-config-mismatch:{config}")

    gitlinks = sorted(entry.path for entry in entries if entry.mode == "160000")
    if gitlinks != [AGENT_CANON_PATH]:
        fail(f"agent-canon-gitlink-set-mismatch:{gitlinks}")

    gitlink = by_path.get(AGENT_CANON_PATH)
    if gitlink is None or gitlink.mode != "160000":
        fail("agent-canon-gitlink-missing")

    checkout = root / AGENT_CANON_PATH
    if checkout.is_symlink() or (checkout.exists() and not checkout.is_dir()):
        fail("agent-canon-checkout-path-invalid")
    if not (checkout / ".git").exists():
        if checkout.exists() and any(checkout.iterdir()):
            fail("agent-canon-uninitialized-checkout-not-empty")
        return
    result = subprocess.run(
        ["git", "-C", str(checkout), "rev-parse", "--verify", "HEAD^{commit}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"agent-canon-checkout-unreadable:{result.stderr.strip()}")
    checkout_head = result.stdout.strip()
    if checkout_head != gitlink.object_id:
        fail(
            "agent-canon-checkout-pin-mismatch:"
            f"gitlink={gitlink.object_id}:checkout={checkout_head}"
        )


def validate_tree(root: Path, entries: list[Entry]) -> None:
    by_path = {entry.path: entry for entry in entries}
    validate_agent_canon_registration(root, entries)
    for forbidden in sorted(FORBIDDEN_TRACKED_PATHS):
        if forbidden in by_path or any(path.startswith(f"{forbidden}/") for path in by_path):
            fail(f"forbidden-tracked-path:{forbidden}")

    for entry in entries:
        if entry.mode != "120000":
            continue
        target = (root / entry.path).readlink().as_posix()
        if "agent-canon" in target.lower():
            fail(f"runtime-symlink-forbidden:{entry.path}:{target}")

    required_regular = ["AGENTS.md", ".codex/config.toml", "agent-canon-static-seed.json"]
    for path in required_regular:
        entry = by_path.get(path)
        if entry is None:
            fail(f"required-static-file-missing:{path}")
        if entry.mode not in {"100644", "100755"}:
            fail(f"required-static-file-not-regular:{path}:{entry.mode}")


def validate_execution_text(root: Path, entries: list[Entry]) -> None:
    for entry in entries:
        if entry.path in SCAN_EXCLUSIONS or entry.mode not in {"100644", "100755"}:
            continue
        if not is_execution_path(entry.path):
            continue
        path = root / entry.path
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for token in FORBIDDEN_RUNTIME_TEXT:
            if token in text:
                fail(f"forbidden-runtime-reference:{entry.path}:{token}")


def validate_static_seed(root: Path, entries: list[Entry]) -> None:
    by_path = {entry.path: entry for entry in entries}
    config_path = root / ".codex/config.toml"
    with config_path.open("rb") as stream:
        config = tomllib.load(stream)

    registrations = config.get("agents")
    if not isinstance(registrations, dict):
        fail("static-seed-config-missing-agents")

    registered_paths: set[str] = set()
    for name, payload in registrations.items():
        if name in {"max_threads", "max_depth", "job_max_runtime_seconds"}:
            continue
        if not isinstance(payload, dict):
            fail(f"static-seed-agent-invalid:{name}")
        config_file = payload.get("config_file")
        if not isinstance(config_file, str) or not config_file.startswith("agents/"):
            fail(f"static-seed-agent-path-invalid:{name}")
        relative = f".codex/{config_file}"
        entry = by_path.get(relative)
        if entry is None:
            fail(f"static-seed-agent-file-missing:{relative}")
        if entry.mode != "100644":
            fail(f"static-seed-agent-file-not-regular:{relative}:{entry.mode}")
        registered_paths.add(relative)

    actual_paths = {
        entry.path
        for entry in entries
        if entry.path.startswith(".codex/agents/") and entry.path.endswith(".toml")
    }
    if actual_paths != registered_paths:
        missing = sorted(registered_paths - actual_paths)
        extra = sorted(actual_paths - registered_paths)
        fail(f"static-seed-closure-mismatch:missing={missing}:extra={extra}")

    provenance = json.loads((root / "agent-canon-static-seed.json").read_text(encoding="utf-8"))
    expected_keys = {"schema_version", "source_commit", "source_repository"}
    if set(provenance) != expected_keys:
        fail("static-seed-provenance-key-set")
    if provenance.get("schema_version") != 1:
        fail("static-seed-provenance-schema")
    if provenance.get("source_repository") != "iwashita-nozomu/agent-canon":
        fail("static-seed-provenance-source")
    source_commit = provenance.get("source_commit")
    if not isinstance(source_commit, str) or len(source_commit) not in {40, 64}:
        fail("static-seed-provenance-commit")
    if any(character not in "0123456789abcdef" for character in source_commit):
        fail("static-seed-provenance-commit")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    if not (root / ".git").exists():
        fail(f"not-a-git-worktree:{root}")
    entries = tracked_entries(root)
    validate_tree(root, entries)
    validate_execution_text(root, entries)
    validate_static_seed(root, entries)
    print("RUNTIME_INDEPENDENCE=pass")


if __name__ == "__main__":
    main()
