#!/usr/bin/env python3
# @dependency-start
# contract tool
# responsibility Provides the parent-root adapter to the canonical shared-surface manifest tool.
# upstream design ../../vendor/agent-canon/documents/runtime/shared-runtime-surfaces.toml machine-readable root-view contract
# upstream implementation ../../vendor/agent-canon/tools/agent_tools/surface_manifest.py canonical manifest implementation
# downstream implementation ../../AGENTS.md parent structure and root-view routing
# @dependency-end
"""Invoke the canonical shared-surface manifest tool from a parent root."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def repository_root() -> Path:
    """Return the parent repository root that owns this adapter."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        capture_output=True,
        text=True,
    )
    return Path(result.stdout.strip()).resolve()


def main() -> int:
    """Route the invocation through the typed AgentCanon source-root resolver."""
    root = repository_root()
    arguments = list(sys.argv[1:])
    if not any(argument == "--root" or argument.startswith("--root=") for argument in arguments):
        arguments[0:0] = ["--root", str(root)]
    if not any(argument == "--prefix" or argument.startswith("--prefix=") for argument in arguments):
        arguments[0:0] = ["--prefix", "vendor/agent-canon"]
    pythonpath = os.pathsep.join(
        part
        for part in (str(root / "vendor/agent-canon/tools"), str(root / "tools"), os.environ.get("PYTHONPATH", ""))
        if part
    )
    environment = os.environ.copy()
    environment["PYTHONPATH"] = pythonpath
    command = [
        sys.executable,
        "-m",
        "agent_tools.agent_canon_source_root",
        "exec",
        "tools/agent_tools/surface_manifest.py",
        *arguments,
    ]
    return subprocess.run(command, cwd=root, env=environment, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
