"""Tests for offline parent-project initialization and validation."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def run(
    args: list[str], cwd: Path, env: dict[str, str] | None = None, *, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args, cwd=cwd, env=env, check=check, capture_output=True, text=True
    )


def clone_current(tmp_path: Path) -> Path:
    clone = tmp_path / "clone"
    ignored = shutil.ignore_patterns(
        ".git",
        "workspace",
        ".pytest_cache",
        ".ruff_cache",
        "build",
        ".state",
        "dist",
        "logs",
        "reports",
    )
    shutil.copytree(REPO_ROOT, clone, symlinks=True, ignore=ignored)
    run(["git", "init", "--quiet"], clone)
    run(["git", "config", "user.email", "test@localhost"], clone)
    run(["git", "config", "user.name", "Test"], clone)
    run(["git", "add", "--all"], clone)
    run(["git", "commit", "--quiet", "-m", "fixture"], clone)
    return clone


def test_bootstrap_is_local_and_idempotent(tmp_path: Path) -> None:
    clone = clone_current(tmp_path)
    env = os.environ.copy()
    env.update(
        {
            "GIT_ALLOW_PROTOCOL": "file",
            "GIT_TERMINAL_PROMPT": "0",
            "HTTPS_PROXY": "http://127.0.0.1:9",
            "HTTP_PROXY": "http://127.0.0.1:9",
        }
    )

    preview = run(
        [
            "bash",
            "scripts/start_repository.sh",
            "--project-slug",
            "seeded-project",
            "--display-name",
            "Seeded Project",
            "--dry-run",
        ],
        clone,
        env,
    )
    assert "template_bootstrap=local_offline" in preview.stdout
    assert "project_runtime=source_free" in preview.stdout
    assert "start_repository_mode=dry_run_only" in preview.stdout

    result = run(
        [
            "bash",
            "scripts/start_repository.sh",
            "--project-slug",
            "seeded-project",
            "--display-name",
            "Seeded Project",
            "--skip-preflight-dry-run",
        ],
        clone,
        env,
    )
    assert "project_runtime=source_free" in result.stdout
    assert "start_repository_init=pass" in result.stdout
    assert not (clone / ".gitmodules").exists()
    assert not (clone / "vendor/agent-canon").exists()
    assert not (clone / ".codex").exists()
    assert not (clone / "AGENTS.md").is_symlink()

    before = run(["git", "diff", "--binary"], clone).stdout
    second = run(
        [
            "bash",
            "scripts/init_from_template.sh",
            "--project-slug",
            "seeded-project",
            "--display-name",
            "Seeded Project",
            "--force",
        ],
        clone,
        env,
    )
    after = run(["git", "diff", "--binary"], clone).stdout
    assert "changed_files=0" in second.stdout
    assert before == after


def test_unknown_option_is_rejected(tmp_path: Path) -> None:
    clone = clone_current(tmp_path)
    result = run(
        [
            "bash",
            "scripts/init_from_template.sh",
            "--project-slug",
            "seeded-project",
            "--unknown-option",
        ],
        clone,
        check=False,
    )
    assert result.returncode == 2
    assert "Unknown option" in result.stderr


def test_validate_only_runs_project_owned_checks_and_is_read_only(tmp_path: Path) -> None:
    clone = clone_current(tmp_path)
    make = tmp_path / "make"
    make.write_text(
        "#!/usr/bin/env bash\n"
        "echo make:$@\n"
        "case \"$1\" in\n"
        "  runtime-independence-check|docs-check|github-workflow-check|fresh-clone-check) exit 0 ;;\n"
        "esac\n"
        "exit 2\n",
        encoding="utf-8",
    )
    make.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:{env['PATH']}"
    result = run(["bash", "scripts/start_repository.sh", "--validate-only"], clone, env)
    for target in (
        "runtime-independence-check",
        "docs-check",
        "github-workflow-check",
        "fresh-clone-check",
    ):
        assert f"make:{target}" in result.stdout
    assert "start_repository_validation=pass" in result.stdout
    assert run(["git", "status", "--short"], clone).stdout == ""


def test_validate_only_refuses_check_side_effects(tmp_path: Path) -> None:
    clone = clone_current(tmp_path)
    make = tmp_path / "make"
    make.write_text(
        "#!/usr/bin/env bash\n"
        "if [[ \"$1\" == \"docs-check\" ]]; then printf drift > drift.txt; fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    make.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{tmp_path}:{env['PATH']}"
    result = run(
        ["bash", "scripts/start_repository.sh", "--validate-only"],
        clone,
        env,
        check=False,
    )
    assert result.returncode == 1
    assert "detected worktree drift" in result.stderr
