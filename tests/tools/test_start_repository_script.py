# @dependency-start
# responsibility Tests repository bootstrap wrapper compatibility with GitHub-first AgentCanon submodule updates.
# upstream implementation ../../scripts/init_from_template.sh seeds local AgentCanon compatibility remotes.
# upstream implementation ../../scripts/start_repository.sh wraps initialization and freshness checks.
# upstream design ../../vendor/agent-canon/documents/github-first-module-and-devcontainer-policy.md defines AgentCanon submodule ownership.
# @dependency-end
"""Tests for the start repository wrapper script."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def run(
    args: list[str],
    cwd: Path,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a command and capture text output."""
    return subprocess.run(
        args,
        cwd=cwd,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )


def test_start_repository_wrapper_seeds_agent_canon_without_subtree(tmp_path: Path) -> None:
    """The wrapper preserves dry-run safety and no-subtree seeding."""
    clone_dir = tmp_path / "clone"
    git_root = tmp_path / "git"
    missing_git_exec = tmp_path / "missing-git-exec"
    git_root.mkdir()
    missing_git_exec.mkdir()

    run(["git", "clone", "--no-local", str(REPO_ROOT), str(clone_dir)], cwd=tmp_path)
    for child in clone_dir.iterdir():
        if child.name == ".git":
            continue
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
            continue
        child.unlink()
    shutil.copytree(
        REPO_ROOT,
        clone_dir,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(".git"),
        symlinks=True,
    )

    env = os.environ.copy()
    env["TEMPLATE_BARE_GIT_ROOT"] = str(git_root)
    env["GIT_EXEC_PATH"] = str(missing_git_exec)
    agent_canon_bare = git_root / "seeded-project-agent-canon.git"

    dry_run = run(
        [
            "bash",
            "scripts/start_repository.sh",
            "--project-slug",
            "seeded-project",
            "--display-name",
            "Seeded Project",
            "--dry-run",
        ],
        cwd=clone_dir,
        env=env,
    )

    assert "would seed agent_canon_bare_repo=" in dry_run.stdout
    assert (
        "would prepare agent_canon_proposal_branch=canon-proposal/seeded-project"
        in dry_run.stdout
    )
    assert "start_repository_mode=dry_run_only" in dry_run.stdout
    assert not agent_canon_bare.exists()

    result = run(
        [
            "bash",
            "scripts/start_repository.sh",
            "--project-slug",
            "seeded-project",
            "--display-name",
            "Seeded Project",
            "--skip-preflight-dry-run",
            "--force",
        ],
        cwd=clone_dir,
        env=env,
    )

    assert "agent_canon_seed_method=" in result.stdout
    assert "agent_canon_proposal_branch=canon-proposal/seeded-project" in result.stdout
    assert "agent_canon_latest=" in result.stdout
    assert "start_repository_init=pass" in result.stdout

    run(
        [
            "git",
            f"--git-dir={agent_canon_bare}",
            "rev-parse",
            "--verify",
            "refs/heads/main",
        ],
        cwd=clone_dir,
    )
    run(
        [
            "git",
            f"--git-dir={agent_canon_bare}",
            "rev-parse",
            "--verify",
            "refs/heads/canon-proposal/seeded-project",
        ],
        cwd=clone_dir,
    )
    remote_url = run(["git", "remote", "get-url", "agent-canon"], cwd=clone_dir)
    assert remote_url.stdout.strip() == str(agent_canon_bare)
    proposal_branch = run(["git", "config", "--get", "agent-canon.proposalBranch"], cwd=clone_dir)
    assert proposal_branch.stdout.strip() == "canon-proposal/seeded-project"
