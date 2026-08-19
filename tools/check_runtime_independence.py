#!/usr/bin/env python3
"""Validate exact AgentCanon registration and bounded live Codex views."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Never


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
AGENT_CANON_RUNTIME_SYMLINKS = {
    "AGENTS.md": "vendor/agent-canon/ROOT_AGENTS.md",
    ".codex/config.toml": "../vendor/agent-canon/.codex/config.toml",
    ".codex/agents": "../vendor/agent-canon/.codex/agents",
    ".codex/hooks.json": "../vendor/agent-canon/.codex/hooks.json",
    ".codex/hooks": "../vendor/agent-canon/.codex/hooks",
}

FORBIDDEN_TRACKED_PATHS = {
    ".agent-canon/update-state.toml",
    ".github/scripts/checkout_agent_canon_submodule.sh",
    ".github/workflows/agent-coordination.yml",
    ".github/workflows/agent-improvement-guide.yml",
    "agent-canon-static-seed.json",
    "documents/design/template-static-seed-import.md",
    "tests/agent_tools",
    "tests/fixtures/static-seed-c5fa3a22",
    "tools/agent-canon",
    "tools/import_agent_canon_static_seed.py",
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


def fail(message: str) -> Never:
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


def read_link(root: Path, path: str) -> str:
    try:
        return (root / path).readlink().as_posix()
    except OSError as exc:
        fail(f"live-view-unreadable:{path}:{exc}")


def validate_live_projection(root: Path, entries: list[Entry]) -> None:
    by_path = {entry.path: entry for entry in entries}

    copied_agent_paths = sorted(
        path for path in by_path if path.startswith(".codex/agents/")
    )
    if copied_agent_paths:
        fail(f"copied-agent-definition:{copied_agent_paths[0]}")

    for path, expected_target in AGENT_CANON_RUNTIME_SYMLINKS.items():
        entry = by_path.get(path)
        if entry is None:
            fail(f"required-live-view-missing:{path}")
        if entry.mode != "120000":
            fail(f"required-live-view-not-symlink:{path}:{entry.mode}")
        actual_target = read_link(root, path)
        if actual_target != expected_target:
            fail(
                "required-live-view-target-mismatch:"
                f"{path}:expected={expected_target}:actual={actual_target}"
            )

    for entry in entries:
        if entry.mode != "120000" or entry.path in AGENT_CANON_RUNTIME_SYMLINKS:
            continue
        target = read_link(root, entry.path)
        if "agent-canon" in target.casefold():
            fail(f"unmanaged-agent-canon-symlink:{entry.path}:{target}")


def validate_tree(root: Path, entries: list[Entry]) -> None:
    by_path = {entry.path: entry for entry in entries}
    validate_agent_canon_registration(root, entries)

    for forbidden in sorted(FORBIDDEN_TRACKED_PATHS):
        if forbidden in by_path or any(
            path.startswith(f"{forbidden}/") for path in by_path
        ):
            fail(f"forbidden-tracked-path:{forbidden}")

    validate_live_projection(root, entries)


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
    print("RUNTIME_INDEPENDENCE=pass")


if __name__ == "__main__":
    main()
