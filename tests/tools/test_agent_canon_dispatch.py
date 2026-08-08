"""Integration checks for the public AgentCanon source-root dispatch routes."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DISPATCHER = ROOT / "tools/agent-canon/agent_tools/agent_canon_source_root.py"


def _dispatch(*command: str) -> subprocess.CompletedProcess[str]:
    """Run a public command through the repository source-root resolver."""
    return subprocess.run(
        [sys.executable, str(DISPATCHER), "exec", *command],
        cwd=ROOT,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )


def test_public_dispatcher_entrypoints_are_executable() -> None:
    """The five public source entrypoints retain executable permissions."""
    entrypoints = (
        ROOT / "vendor/agent-canon/tools/agent_tools/surface_manifest.py",
        ROOT / "vendor/agent-canon/tools/agent_tools/dependency_module_change.py",
        ROOT / "vendor/agent-canon/tools/update_agent_canon.sh",
        ROOT / "vendor/agent-canon/tools/ci/check_agent_canon_latest.sh",
        ROOT / "vendor/agent-canon/tools/ci/check_agent_canon_pr.sh",
    )
    assert all(path.is_file() and os.access(path, os.X_OK) for path in entrypoints)


def test_public_dispatcher_help_routes_do_not_mutate_checkout() -> None:
    """Help/usage probes resolve through AgentCanon without changing the checkout."""
    before = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    probes = (
        ("tools/agent_tools/surface_manifest.py", "--help", 0, "usage:"),
        ("tools/agent_tools/dependency_module_change.py", "--help", 0, "usage:"),
        ("tools/update_agent_canon.sh", 0, "Usage:"),
        ("tools/ci/check_agent_canon_latest.sh", "--help", 0, "agent_canon_plan_route="),
        ("tools/ci/check_agent_canon_pr.sh", "--help", 2, "usage:"),
    )
    for probe in probes:
        *command, expected_returncode, marker = probe
        result = _dispatch(*command)
        assert result.returncode == expected_returncode, result.stdout + result.stderr
        assert marker.lower() in (result.stdout + result.stderr).lower()
    after = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert after == before
