"""Tests for offline template initialization and the validation wrapper."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT_CANON_PIN = "0ea5bb6d5d0bfc2e027698612aeb6fc5a3c8b0c2"
AGENT_CANON_GITMODULES = """[submodule "vendor/agent-canon"]
\tpath = vendor/agent-canon
\turl = https://github.com/iwashita-nozomu/agent-canon.git
\tbranch = main
"""


def run(
    args: list[str], cwd: Path, env: dict[str, str] | None = None, *, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args, cwd=cwd, env=env, check=check, capture_output=True, text=True
    )


def clone_current(tmp_path: Path) -> Path:
    clone = tmp_path / "clone"
    run(["git", "clone", "--no-local", str(REPO_ROOT), str(clone)], tmp_path)
    return clone


def offline_env() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "GIT_ALLOW_PROTOCOL": "file",
            "GIT_TERMINAL_PROMPT": "0",
            "HTTPS_PROXY": "http://127.0.0.1:9",
            "HTTP_PROXY": "http://127.0.0.1:9",
        }
    )
    return env


def registration_snapshot(root: Path) -> tuple[str, ...]:
    entries: list[tuple[str, str, str]] = []
    for line in run(["git", "ls-files", "-s"], root).stdout.splitlines():
        metadata, path = line.split("\t", 1)
        mode, object_id, _stage = metadata.split()
        entries.append((mode, object_id, path))

    metadata = [entry for entry in entries if entry[2] == ".gitmodules"]
    gitlinks = [entry for entry in entries if entry[0] == "160000"]
    if not metadata and not gitlinks:
        assert not (root / ".gitmodules").exists()
        assert not (root / "vendor/agent-canon").exists()
        return ("absent",)

    assert len(metadata) == 1
    assert metadata[0][0] == "100644"
    assert (root / ".gitmodules").is_file()
    assert run(
        [
            "git",
            "config",
            "--file",
            ".gitmodules",
            "--get",
            "submodule.vendor/agent-canon.path",
        ],
        root,
    ).stdout.strip() == "vendor/agent-canon"
    assert run(
        [
            "git",
            "config",
            "--file",
            ".gitmodules",
            "--get",
            "submodule.vendor/agent-canon.url",
        ],
        root,
    ).stdout.strip() == "https://github.com/iwashita-nozomu/agent-canon.git"
    assert run(
        [
            "git",
            "config",
            "--file",
            ".gitmodules",
            "--get",
            "submodule.vendor/agent-canon.branch",
        ],
        root,
    ).stdout.strip() == "main"
    assert len(gitlinks) == 1
    assert gitlinks[0][2] == "vendor/agent-canon"

    checkout = root / "vendor/agent-canon"
    assert not (checkout / ".git").exists()
    assert not checkout.exists() or not any(checkout.iterdir())
    return ("exact", gitlinks[0][1])


def run_bootstrap(clone: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return run(
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


def test_bootstrap_is_local_and_idempotent(tmp_path: Path) -> None:
    clone = clone_current(tmp_path)
    env = offline_env()
    registration_before = registration_snapshot(clone)

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
    assert "start_repository_mode=dry_run_only" in preview.stdout

    result = run_bootstrap(clone, env)
    assert "static_seed=repository_owned_regular_files" in result.stdout
    assert "start_repository_init=pass" in result.stdout
    assert registration_snapshot(clone) == registration_before
    assert not (clone / ".agent-canon").exists()

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


def test_bootstrap_preserves_exact_inert_registration(tmp_path: Path) -> None:
    clone = clone_current(tmp_path)
    registration_before = registration_snapshot(clone)
    if registration_before == ("absent",):
        run(["git", "config", "user.email", "test@localhost"], clone)
        run(["git", "config", "user.name", "Test"], clone)
        (clone / ".gitmodules").write_text(AGENT_CANON_GITMODULES, encoding="utf-8")
        run(["git", "add", ".gitmodules"], clone)
        run(
            [
                "git",
                "update-index",
                "--add",
                "--cacheinfo",
                f"160000,{AGENT_CANON_PIN},vendor/agent-canon",
            ],
            clone,
        )
        run(["git", "commit", "-m", "Register AgentCanon source identity"], clone)
        (clone / "vendor/agent-canon").mkdir(parents=True)
        registration_before = registration_snapshot(clone)

    assert registration_before[0] == "exact"
    result = run_bootstrap(clone, offline_env())
    assert "start_repository_init=pass" in result.stdout
    assert registration_snapshot(clone) == registration_before
    assert not (clone / ".agent-canon").exists()


def test_unknown_legacy_option_remains_rejected(tmp_path: Path) -> None:
    clone = clone_current(tmp_path)
    result = run(
        [
            "bash",
            "scripts/init_from_template.sh",
            "--project-slug",
            "seeded-project",
            "--skip-agent-canon-check",
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
