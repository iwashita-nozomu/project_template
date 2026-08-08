# @dependency-start
# contract test
# responsibility Tests test start repository script behavior.
# upstream implementation ../../scripts/start_repository.sh repository start wrapper
# upstream design ../../documents/contracts/template-bootstrap.md bootstrap contract
# @dependency-end
"""Tests for the start repository wrapper script."""

from __future__ import annotations

import os
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


def test_start_repository_wrapper_keeps_agent_canon_github_submodule(tmp_path: Path) -> None:
    """The wrapper preserves dry-run safety and does not seed local AgentCanon remotes."""
    clone_dir = tmp_path / "clone"
    git_root = tmp_path / "git"
    missing_git_exec = tmp_path / "missing-git-exec"
    git_root.mkdir()
    missing_git_exec.mkdir()

    run(["git", "clone", "--no-local", str(REPO_ROOT), str(clone_dir)], cwd=tmp_path)
    run(
        ["rsync", "-a", "--delete", "--exclude", ".git", f"{REPO_ROOT}/", str(clone_dir)],
        cwd=tmp_path,
    )

    env = os.environ.copy()
    env["TEMPLATE_BARE_GIT_ROOT"] = str(git_root)
    env["GIT_EXEC_PATH"] = str(missing_git_exec)

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

    assert "would keep agent_canon_source=github_submodule" in dry_run.stdout
    assert "start_repository_mode=dry_run_only" in dry_run.stdout

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

    assert "agent_canon_source=github_submodule" in result.stdout
    assert "agent_canon_preflight=blocked_init_force" in result.stdout
    assert (
        "agent_canon_preflight_reason="
        "wrapper_skips_make_agent-canon-update_when_init_force_is_requested" in result.stdout
    )
    assert "start_repository_init=pass" in result.stdout
    assert not (git_root / "seeded-project-agent-canon.git").exists()


def test_init_from_template_unknown_python_package_option(tmp_path: Path) -> None:
    """Unknown options now stay unknown in template init."""
    clone_dir = tmp_path / "clone"
    git_root = tmp_path / "git"
    missing_git_exec = tmp_path / "missing-git-exec"
    run(["git", "clone", "--no-local", str(REPO_ROOT), str(clone_dir)], cwd=tmp_path)
    run(
        ["rsync", "-a", "--delete", "--exclude", ".git", f"{REPO_ROOT}/", str(clone_dir)],
        cwd=tmp_path,
    )

    env = os.environ.copy()
    env["TEMPLATE_BARE_GIT_ROOT"] = str(git_root)
    env["GIT_EXEC_PATH"] = str(missing_git_exec)
    result = subprocess.run(
        [
            "bash",
            "scripts/init_from_template.sh",
            "--project-slug",
            "seeded-project",
            "--python-package",
            "seeded_package",
        ],
        cwd=clone_dir,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "Unknown option: --python-package" in result.stderr


def test_start_repository_validate_only_is_read_only(tmp_path: Path) -> None:
    """validate-only must be read-only and only run freshness checks."""
    clone_dir = tmp_path / "clone"
    run(["git", "clone", "--no-local", str(REPO_ROOT), str(clone_dir)], cwd=tmp_path)
    run(["rsync", "-a", "--delete", "--exclude", ".git", f"{REPO_ROOT}/", str(clone_dir)], cwd=tmp_path)
    run(["git", "-C", str(clone_dir), "config", "user.email", "ci@localhost"], cwd=clone_dir)
    run(["git", "-C", str(clone_dir), "config", "user.name", "CI"], cwd=clone_dir)
    run(["git", "-C", str(clone_dir), "add", "--all"], cwd=clone_dir)
    status = run(["git", "-C", str(clone_dir), "status", "--short"], cwd=clone_dir)
    if status.stdout.strip():
        run(
            ["git", "-C", str(clone_dir), "commit", "--allow-empty", "-m", "sync working copy"],
            cwd=clone_dir,
        )

    make = tmp_path / "make"
    make.write_text(
        "#!/usr/bin/env bash\n"
        "echo \"make:$@\"\n"
        "if [[ \"$1\" == \"agent-canon-latest-check\" || \"$1\" == \"fresh-clone-check\" ]]; then\n"
        "  exit 0\n"
        "fi\n"
        "echo \"unexpected make command\" >&2\n"
        "exit 2\n",
        encoding="utf-8",
    )
    make.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:{env['PATH']}"
    result = run(
        ["bash", "scripts/start_repository.sh", "--validate-only"],
        cwd=clone_dir,
        env=env,
    )

    assert "make:agent-canon-latest-check" in result.stdout
    assert "make:fresh-clone-check" in result.stdout
    assert "start_repository_mode=validate_only_readonly" in result.stdout
    assert "start_repository_validation=pass" in result.stdout


def test_start_repository_validate_only_refuses_agent_canon_latest_side_effects(tmp_path: Path) -> None:
    """validate-only fails if any command writes worktree changes."""
    clone_dir = tmp_path / "clone"
    run(["git", "clone", "--no-local", str(REPO_ROOT), str(clone_dir)], cwd=tmp_path)
    run(
        ["rsync", "-a", "--delete", "--exclude", ".git", f"{REPO_ROOT}/", str(clone_dir)],
        cwd=tmp_path,
    )
    run(["git", "-C", str(clone_dir), "config", "user.email", "ci@localhost"], cwd=clone_dir)
    run(["git", "-C", str(clone_dir), "config", "user.name", "CI"], cwd=clone_dir)
    run(["git", "-C", str(clone_dir), "add", "--all"], cwd=clone_dir)
    status = run(["git", "-C", str(clone_dir), "status", "--short"], cwd=clone_dir)
    if status.stdout.strip():
        run(
            ["git", "-C", str(clone_dir), "commit", "--allow-empty", "-m", "sync working copy"],
            cwd=clone_dir,
        )

    make = tmp_path / "make"
    make.write_text(
        "#!/usr/bin/env bash\n"
        "echo \"make:$@\"\n"
        "if [[ \"$1\" == \"agent-canon-latest-check\" ]]; then\n"
        "  mkdir -p side_effects\n"
        "  printf ok > side_effects/agent-canon-latest-check.txt\n"
        "  exit 0\n"
        "fi\n"
        "if [[ \"$1\" == \"fresh-clone-check\" ]]; then\n"
        "  exit 0\n"
        "fi\n"
        "echo \"unexpected make command\" >&2\n"
        "exit 2\n",
        encoding="utf-8",
    )
    make.chmod(0o755)

    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:{env['PATH']}"
    result = subprocess.run(
        ["bash", "scripts/start_repository.sh", "--validate-only"],
        cwd=clone_dir,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "--validate-only detected worktree drift after validation; refuse to report pass" in result.stderr
    assert "start_repository_mode=validate_only_readonly" not in result.stdout
    assert "start_repository_validation=pass" not in result.stdout
    assert "make:agent-canon-update" not in result.stdout
    assert (clone_dir / "side_effects/agent-canon-latest-check.txt").exists()
