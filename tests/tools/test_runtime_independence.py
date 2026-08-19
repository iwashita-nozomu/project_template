"""Focused tests for the self-contained repository guard."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "tools/check_runtime_independence.py"
AGENT_CANON_PIN = "1" * 40
GITMODULES = """[submodule "vendor/agent-canon"]
\tpath = vendor/agent-canon
\turl = https://github.com/iwashita-nozomu/agent-canon.git
\tbranch = main
"""


def run(args: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=check, capture_output=True, text=True)


def make_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "fixture"
    (root / "tools").mkdir(parents=True)
    (root / ".codex/agents").mkdir(parents=True)
    (root / "scripts").mkdir()
    shutil.copy2(CHECKER, root / "tools/check_runtime_independence.py")
    (root / "AGENTS.md").write_text("# instructions\n", encoding="utf-8")
    (root / "Makefile").write_text("check:\n\t@true\n", encoding="utf-8")
    (root / ".codex/config.toml").write_text(
        "[agents]\nmax_threads = 1\n\n"
        "[agents.worker]\n"
        'description = "worker"\n'
        'config_file = "agents/worker.toml"\n',
        encoding="utf-8",
    )
    (root / ".codex/agents/worker.toml").write_text(
        'name = "worker"\ndescription = "worker"\n', encoding="utf-8"
    )
    (root / "agent-canon-static-seed.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_repository": "iwashita-nozomu/agent-canon",
                "source_commit": "0" * 40,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (root / ".gitmodules").write_text(GITMODULES, encoding="utf-8")
    run(["git", "init"], root)
    run(["git", "config", "user.email", "test@localhost"], root)
    run(["git", "config", "user.name", "Test"], root)
    run(["git", "add", "--all"], root)
    run(
        [
            "git",
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{AGENT_CANON_PIN},vendor/agent-canon",
        ],
        root,
    )
    return root


def check(root: Path) -> subprocess.CompletedProcess[str]:
    return run(
        ["python3", "tools/check_runtime_independence.py", "--root", str(root)],
        root,
        check=False,
    )


def test_minimal_regular_static_seed_passes(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    result = check(root)
    assert result.returncode == 0, result.stderr
    assert "RUNTIME_INDEPENDENCE=pass" in result.stdout


def test_missing_submodule_metadata_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    run(["git", "rm", "--cached", ".gitmodules"], root)
    result = check(root)
    assert result.returncode == 1
    assert "agent-canon-submodule-metadata-missing" in result.stderr


def test_wrong_submodule_url_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    (root / ".gitmodules").write_text(
        GITMODULES.replace(
            "https://github.com/iwashita-nozomu/agent-canon.git",
            "https://example.invalid/agent-canon.git",
        ),
        encoding="utf-8",
    )
    run(["git", "add", ".gitmodules"], root)
    result = check(root)
    assert result.returncode == 1
    assert "agent-canon-submodule-config-mismatch" in result.stderr


def test_additional_gitlink_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    run(
        [
            "git",
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{AGENT_CANON_PIN},vendor/other",
        ],
        root,
    )
    result = check(root)
    assert result.returncode == 1
    assert "agent-canon-gitlink-set-mismatch" in result.stderr


def test_missing_agent_canon_gitlink_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    run(["git", "update-index", "--force-remove", "vendor/agent-canon"], root)
    result = check(root)
    assert result.returncode == 1
    assert "agent-canon-gitlink-set-mismatch" in result.stderr


def test_initialized_checkout_must_match_gitlink(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    checkout = root / "vendor/agent-canon"
    checkout.mkdir(parents=True)
    run(["git", "init"], checkout)
    run(["git", "config", "user.email", "test@localhost"], checkout)
    run(["git", "config", "user.name", "Test"], checkout)
    (checkout / "README.md").write_text("source\n", encoding="utf-8")
    run(["git", "add", "README.md"], checkout)
    run(["git", "commit", "-m", "fixture"], checkout)
    result = check(root)
    assert result.returncode == 1
    assert "agent-canon-checkout-pin-mismatch" in result.stderr


def test_uninitialized_checkout_directory_must_be_empty(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    checkout = root / "vendor/agent-canon"
    checkout.mkdir(parents=True)
    (checkout / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")
    result = check(root)
    assert result.returncode == 1
    assert "agent-canon-uninitialized-checkout-not-empty" in result.stderr


def test_agent_canon_root_symlink_remains_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    (root / "tools/agent-canon").symlink_to("../vendor/agent-canon/tools")
    run(["git", "add", "tools/agent-canon"], root)
    result = check(root)
    assert result.returncode == 1
    assert "forbidden-tracked-path:tools/agent-canon" in result.stderr


def test_parent_agent_tools_test_namespace_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    test_path = root / "tests/agent_tools/test_runtime.py"
    test_path.parent.mkdir(parents=True)
    test_path.write_text("def test_runtime():\n    assert True\n", encoding="utf-8")
    run(["git", "add", str(test_path.relative_to(root))], root)
    result = check(root)
    assert result.returncode == 1
    assert "forbidden-tracked-path:tests/agent_tools" in result.stderr


def test_runtime_dispatch_reference_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    (root / "scripts/bootstrap.sh").write_text(
        "python3 agent_canon_source_root.py exec something\n", encoding="utf-8"
    )
    run(["git", "add", "scripts/bootstrap.sh"], root)
    result = check(root)
    assert result.returncode == 1
    assert "forbidden-runtime-reference:scripts/bootstrap.sh" in result.stderr


def test_legacy_submodule_strategy_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    (root / "scripts/bootstrap.sh").write_text(
        "submodule_strategy=github_submodule\n", encoding="utf-8"
    )
    run(["git", "add", "scripts/bootstrap.sh"], root)
    result = check(root)
    assert result.returncode == 1
    assert "forbidden-runtime-reference:scripts/bootstrap.sh" in result.stderr


def test_seed_registration_requires_regular_file(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    (root / ".codex/agents/worker.toml").unlink()
    (root / ".codex/agents/worker.toml").symlink_to("missing.toml")
    run(["git", "add", ".codex/agents/worker.toml"], root)
    result = check(root)
    assert result.returncode == 1
    assert "static-seed-agent-file-not-regular" in result.stderr
