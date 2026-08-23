#!/usr/bin/env python3
"""Check that the template has no live AgentCanon source dependency.

The template may document an optional, user-managed AgentCanon development
checkout, but a normal clone must be self-contained. This check therefore
looks only at committed repository structure and files that can affect normal
execution. It does not inspect an ignored development workspace or use the
network.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Never


@dataclass(frozen=True)
class Entry:
    """One index entry needed for structural boundary checks."""

    mode: str
    path: str


# These are structural re-entry points. A source-free template must not retain
# a submodule registration, a gitlink, or a tracked AgentCanon source
# checkout/projection under any spelling.
AGENT_CANON_PATH_MARKER = re.compile(r"agent[\W_]*canon", re.IGNORECASE)
FORBIDDEN_TRACKED_PATH_MARKERS = (
    "agent-canon-static-seed",
    "agent_canon_static_seed",
    "import_agent_canon_static_seed",
    "agent-canon-source",
    "agent_canon_source",
    ".agent-canon",
)

# Only files that can participate in normal project execution are scanned for
# runtime references. Documentation and user-managed development helpers are
# intentionally outside this set; this avoids turning a boundary check into a
# repository-wide prose linter.
EXECUTION_PATHS = (
    "Makefile",
    "bootstrap.sh",
    "pyproject.toml",
    ".codex/",
    "scripts/",
    "docker/",
    ".devcontainer/",
    ".github/workflows/",
    ".github/scripts/",
    ".vscode/",
)

# These tokens represent a runtime/source resolver, credential flow, or the
# retired vendored/static-seed route. The generic repository name is not
# forbidden here because an explicit development helper may mention it while
# remaining outside the normal runtime path.
FORBIDDEN_RUNTIME_TEXT = (
    "vendor/agent-canon",
    "tools/agent-canon",
    "PYTHONPATH=vendor/agent-canon",
    "agent_canon_source",
    "agent-canon-source",
    "source_resolver",
    "source-resolver",
    "checkout_agent_canon_submodule",
    "agent-canon-static-seed",
    "agent_canon_static_seed",
    ".agent-canon/docker-compose.generated.yml",
    "AGENT_CANON_READ_TOKEN",
    "AGENT_CANON_REPO_TOKEN",
    "AGENT_CANON_REPO_SSH_KEY",
    "AGENT_CANON_TEMPLATE_SUBMODULE_STRATEGY",
)

SCAN_EXCLUSIONS = {
    "tools/check_runtime_independence.py",
    "docker/check_zero_build_contract.sh",
}


def fail(message: str) -> Never:
    """Emit one stable finding and stop the check."""
    print(f"RUNTIME_INDEPENDENCE_FINDING={message}", file=sys.stderr)
    raise SystemExit(1)


def git(root: Path, *args: str) -> str:
    """Run a read-only Git command in the candidate worktree."""
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
    """Read the candidate's staged paths and modes."""
    output = git(root, "ls-files", "-s", "-z")
    entries: list[Entry] = []
    for record in output.split("\0"):
        if not record:
            continue
        metadata, path = record.split("\t", 1)
        mode, _object_id, _stage = metadata.split()
        entries.append(Entry(mode=mode, path=path))
    return entries


def contains_agent_canon(value: str) -> bool:
    """Return whether a path contains an AgentCanon spelling."""
    return bool(AGENT_CANON_PATH_MARKER.search(value))


def is_execution_path(path: str) -> bool:
    """Return whether a tracked path can affect ordinary execution."""
    return any(path == prefix or path.startswith(prefix) for prefix in EXECUTION_PATHS)


def read_link(root: Path, path: str) -> str:
    """Read one tracked symlink without following its target."""
    try:
        return (root / path).readlink().as_posix()
    except OSError as exc:
        fail(f"symlink-unreadable:{path}:{exc}")


def validate_structure(root: Path, entries: list[Entry]) -> None:
    """Reject submodules, source artifacts, and AgentCanon source links."""
    by_path = {entry.path: entry for entry in entries}

    metadata = by_path.get(".gitmodules")
    if metadata is not None:
        try:
            metadata_text = (root / metadata.path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            fail(f"submodule-metadata-unreadable:.gitmodules:{exc}")
        if contains_agent_canon(metadata_text):
            fail("agent-canon-submodule-forbidden:.gitmodules")

    gitlinks = sorted(
        entry.path
        for entry in entries
        if entry.mode == "160000" and contains_agent_canon(entry.path)
    )
    if gitlinks:
        fail(f"agent-canon-gitlink-forbidden:{gitlinks[0]}")

    for marker in FORBIDDEN_TRACKED_PATH_MARKERS:
        matching = sorted(
            path for path in by_path if marker.casefold() in path.casefold()
        )
        if matching:
            fail(f"forbidden-source-artifact:{matching[0]}")

    for entry in entries:
        if entry.mode != "120000":
            continue
        target = read_link(root, entry.path)
        if contains_agent_canon(entry.path) or contains_agent_canon(target):
            fail(f"agent-canon-source-symlink:{entry.path}:{target}")


def validate_execution_text(root: Path, entries: list[Entry]) -> None:
    """Reject retired AgentCanon source/runtime routes in execution files."""
    for entry in entries:
        if entry.path in SCAN_EXCLUSIONS or entry.mode not in {"100644", "100755"}:
            continue
        if not is_execution_path(entry.path):
            continue
        path = root / entry.path
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        folded_text = text.casefold()
        for token in FORBIDDEN_RUNTIME_TEXT:
            if token.casefold() in folded_text:
                fail(f"forbidden-runtime-reference:{entry.path}:{token}")


def main() -> None:
    """Validate the selected worktree and print a stable pass marker."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    if not (root / ".git").exists():
        fail(f"not-a-git-worktree:{root}")
    entries = tracked_entries(root)
    validate_structure(root, entries)
    validate_execution_text(root, entries)
    print("RUNTIME_INDEPENDENCE=pass")


if __name__ == "__main__":
    main()
