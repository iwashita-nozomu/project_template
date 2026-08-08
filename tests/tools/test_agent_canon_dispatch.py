# @dependency-start
# contract test
# responsibility Verifies Template-owned public AgentCanon dispatcher routes and workflow role forwarding.
# upstream implementation ../../tools/agent-canon/agent_tools/agent_canon_source_root.py resolves source-root command dispatch
# upstream design ../../.github/workflows/agent-coordination.yml forwards specialist role IDs
# @dependency-end
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


def test_coordination_forwards_roles_to_canonical_bootstrap() -> None:
    """Specialist IDs are validated by canonical bootstrap, not a local allowlist."""
    workflow = (ROOT / ".github/workflows/agent-coordination.yml").read_text(
        encoding="utf-8"
    )
    assert 'flags+=(--enable "${role}")' in workflow
    assert "unsupported specialist role" not in workflow
    assert "researcher|research_reviewer|scheduler" not in workflow


def test_template_runtime_projection_paths_exist() -> None:
    """Workflow and editor commands resolve only to checked-in Template paths."""
    for relative in (
        "tools/agent-canon/agent_tools/bootstrap_agent_run.py",
        "tools/agent-canon/agent_tools/validate_role_write_scope.py",
        "tools/agent-canon/agent_tools/check_convention_compliance.py",
        "tools/agent-canon/lib/repo_paths.sh",
    ):
        assert (ROOT / relative).is_file(), relative
    workflow = (ROOT / ".github/workflows/agent-coordination.yml").read_text(
        encoding="utf-8"
    )
    tasks = (ROOT / ".vscode/tasks.json").read_text(encoding="utf-8")
    assert "tools/agent-canon/agent_tools/bootstrap_agent_run.py" in workflow
    assert "tools/agent-canon/agent_tools/validate_role_write_scope.py" in workflow
    assert "tools/agent-canon/lib/repo_paths.sh" in tasks
