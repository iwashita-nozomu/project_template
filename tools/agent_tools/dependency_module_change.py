#!/usr/bin/env python3
# @dependency-start
# contract tool
# responsibility Provides the parent-root adapter to the canonical dependency-module lifecycle tool.
# upstream design ../../vendor/agent-canon/documents/runtime/shared-runtime-surfaces.toml shared tool ownership
# upstream implementation ../../vendor/agent-canon/tools/agent_tools/dependency_module_change.py canonical dependency lifecycle implementation
# downstream implementation ../../AGENTS.md parent dependency clone and workspace route
# @dependency-end
"""Invoke the canonical dependency-module lifecycle tool from a parent root."""

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
    pythonpath = os.pathsep.join(
        part
        for part in (
            str(root / "vendor/agent-canon/tools"),
            str(root / "tools"),
            os.environ.get("PYTHONPATH", ""),
        )
        if part
    )
    environment = os.environ.copy()
    environment["PYTHONPATH"] = pythonpath
    command = [
        sys.executable,
        "-m",
        "agent_tools.agent_canon_source_root",
        "exec",
        "tools/agent_tools/dependency_module_change.py",
        *sys.argv[1:],
    ]
    return subprocess.run(command, cwd=root, env=environment, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
