"""Offline lifecycle tests for the ignored AgentCanon development clone."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DEVELOP_SCRIPT = REPO_ROOT / "scripts/agent-canon-develop.sh"


def run(
    args: list[str], cwd: Path, *, check: bool = True
) -> subprocess.CompletedProcess[str]:
    """Run a fixture command and capture its output."""
    return subprocess.run(args, cwd=cwd, check=check, capture_output=True, text=True)


def git(args: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run Git in a fixture checkout."""
    return run(["git", *args], cwd, check=check)


def make_project(tmp_path: Path) -> Path:
    """Create a minimal project containing the lifecycle helper."""
    root = tmp_path / "project"
    (root / "scripts").mkdir(parents=True)
    target = root / "scripts/agent-canon-develop.sh"
    target.write_bytes(DEVELOP_SCRIPT.read_bytes())
    target.chmod(0o755)
    git(["init"], root)
    git(["config", "user.email", "test@localhost"], root)
    git(["config", "user.name", "Test"], root)
    git(["add", "scripts/agent-canon-develop.sh"], root)
    git(["commit", "-m", "project fixture"], root)
    return root


def make_remote(tmp_path: Path) -> Path:
    """Create a local bare AgentCanon-shaped remote with a main branch."""
    seed = tmp_path / "seed"
    remote = tmp_path / "agent-canon.git"
    seed.mkdir()
    git(["init", "--bare", str(remote)], tmp_path)
    git(["init"], seed)
    git(["config", "user.email", "test@localhost"], seed)
    git(["config", "user.name", "Test"], seed)
    (seed / "README.md").write_text("canonical\n", encoding="utf-8")
    git(["add", "README.md"], seed)
    git(["commit", "-m", "initial"], seed)
    git(["branch", "-M", "main"], seed)
    git(["remote", "add", "origin", str(remote)], seed)
    git(["push", "origin", "main"], seed)
    git(["--git-dir", str(remote), "symbolic-ref", "HEAD", "refs/heads/main"], tmp_path)
    return remote


def invoke(
    project: Path,
    remote: Path,
    *args: str,
    check: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Invoke the copied lifecycle helper against a local remote."""
    env = os.environ.copy()
    env["AGENT_CANON_DEVELOP_REMOTE"] = str(remote)
    return subprocess.run(
        [str(project / "scripts/agent-canon-develop.sh"), *args],
        cwd=project,
        env=env,
        check=check,
        capture_output=True,
        text=True,
    )


def test_clone_status_refresh_and_cleanup_use_task_workspace(tmp_path: Path) -> None:
    """Exercise clone, status, refresh, and safe cleanup end to end."""
    project = make_project(tmp_path)
    remote = make_remote(tmp_path)

    cloned = invoke(project, remote, "clone", "issue-841")
    assert cloned.returncode == 0, cloned.stderr
    clone_root = project / "workspace/agent-canondevelop/issue-841/agent-canon"
    assert clone_root.is_dir()
    assert git(["branch", "--show-current"], clone_root).stdout.strip() == "main"

    status = invoke(project, remote, "status", "issue-841")
    assert status.returncode == 0, status.stderr
    assert "## main...origin/main" in status.stdout

    seed = tmp_path / "seed"
    (seed / "CHANGELOG.md").write_text("refresh\n", encoding="utf-8")
    git(["add", "CHANGELOG.md"], seed)
    git(["commit", "-m", "refresh"], seed)
    git(["push", "origin", "main"], seed)
    refreshed = invoke(project, remote, "refresh", "issue-841")
    assert refreshed.returncode == 0, refreshed.stderr
    assert (clone_root / "CHANGELOG.md").exists() is False

    # Refresh only fetches; cleanup is the lifecycle operation that removes
    # the exact task workspace after verifying a clean, merged checkout.
    cleaned = invoke(project, remote, "cleanup", "issue-841")
    assert cleaned.returncode == 0, cleaned.stderr
    assert not (project / "workspace/agent-canondevelop/issue-841").exists()


def test_cleanup_rejects_dirty_checkout(tmp_path: Path) -> None:
    """Keep a dirty development clone instead of deleting it."""
    project = make_project(tmp_path)
    remote = make_remote(tmp_path)
    assert invoke(project, remote, "clone", "dirty").returncode == 0
    clone_root = project / "workspace/agent-canondevelop/dirty/agent-canon"
    (clone_root / "dirty.txt").write_text("not committed\n", encoding="utf-8")

    result = invoke(project, remote, "cleanup", "dirty")
    assert result.returncode == 1
    assert "checkout is dirty" in result.stderr
    assert clone_root.exists()


def test_cleanup_rejects_head_not_contained_in_origin_main(tmp_path: Path) -> None:
    """Keep a clean but unmerged development clone for review."""
    project = make_project(tmp_path)
    remote = make_remote(tmp_path)
    assert invoke(project, remote, "clone", "unmerged").returncode == 0
    clone_root = project / "workspace/agent-canondevelop/unmerged/agent-canon"
    git(["config", "user.email", "test@localhost"], clone_root)
    git(["config", "user.name", "Test"], clone_root)
    (clone_root / "local.txt").write_text("local\n", encoding="utf-8")
    git(["add", "local.txt"], clone_root)
    git(["commit", "-m", "local-only"], clone_root)

    result = invoke(project, remote, "cleanup", "unmerged")
    assert result.returncode == 1
    assert "not contained in origin/main" in result.stderr
    assert clone_root.exists()


@pytest.mark.parametrize("qualified_task", ["../escape", "task/../../escape", "/tmp/escape"])
def test_task_name_cannot_escape_ignored_workspace(
    tmp_path: Path, qualified_task: str
) -> None:
    """Reject traversal and absolute task names before creating a clone."""
    project = make_project(tmp_path)
    remote = make_remote(tmp_path)
    result = invoke(project, remote, "clone", qualified_task)
    assert result.returncode == 2
    assert "qualified-task" in result.stderr
    assert not (project.parent / "escape").exists()
    assert not (project / "workspace/agent-canondevelop").exists()


def test_symlinked_workspace_boundary_is_rejected(tmp_path: Path) -> None:
    """Reject a workspace symlink that would redirect writes outside the repo."""
    project = make_project(tmp_path)
    remote = make_remote(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (project / "workspace").symlink_to(outside, target_is_directory=True)

    result = invoke(project, remote, "clone", "safe-task")
    assert result.returncode == 1
    assert "symlinked development workspace boundary" in result.stderr
    assert not (outside / "agent-canondevelop").exists()
