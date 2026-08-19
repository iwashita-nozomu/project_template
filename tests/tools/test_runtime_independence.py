"""Focused tests for the self-contained repository guard."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

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
    run(["git", "init"], root)
    run(["git", "config", "user.email", "test@localhost"], root)
    run(["git", "config", "user.name", "Test"], root)
    run(["git", "add", "--all"], root)
    return root


def register_agent_canon(
    root: Path,
    *,
    metadata: str = GITMODULES,
    path: str = "vendor/agent-canon",
    pin: str = AGENT_CANON_PIN,
) -> None:
    (root / ".gitmodules").write_text(metadata, encoding="utf-8")
    run(["git", "add", ".gitmodules"], root)
    run(
        ["git", "update-index", "--add", "--cacheinfo", f"160000,{pin},{path}"],
        root,
    )


def check(root: Path) -> subprocess.CompletedProcess[str]:
    return run(
        ["python3", "tools/check_runtime_independence.py", "--root", str(root)],
        root,
        check=False,
    )


def assert_finding(root: Path, finding: str) -> None:
    result = check(root)
    assert result.returncode == 1
    assert finding in result.stderr


def test_static_seed_without_registration_passes(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    result = check(root)
    assert result.returncode == 0, result.stderr
    assert "RUNTIME_INDEPENDENCE=pass" in result.stdout


def test_exact_agent_canon_registration_passes(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    register_agent_canon(root)
    result = check(root)
    assert result.returncode == 0, result.stderr
    assert "RUNTIME_INDEPENDENCE=pass" in result.stdout


def test_submodule_metadata_without_gitlink_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    (root / ".gitmodules").write_text(GITMODULES, encoding="utf-8")
    run(["git", "add", ".gitmodules"], root)
    assert_finding(root, "agent-canon-gitlink-set-mismatch")


def test_gitlink_without_submodule_metadata_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
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
    assert_finding(root, "agent-canon-submodule-metadata-missing")


def test_malformed_submodule_metadata_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    register_agent_canon(root, metadata='[submodule "vendor/agent-canon"\n')
    assert_finding(root, "agent-canon-submodule-config-unreadable")


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("path = vendor/agent-canon", "path = vendor/other"),
        (
            "url = https://github.com/iwashita-nozomu/agent-canon.git",
            "url = https://example.invalid/agent-canon.git",
        ),
        ("branch = main", "branch = release"),
    ],
)
def test_alternate_submodule_config_is_rejected(
    tmp_path: Path, before: str, after: str
) -> None:
    root = make_fixture(tmp_path)
    register_agent_canon(root, metadata=GITMODULES.replace(before, after))
    assert_finding(root, "agent-canon-submodule-config-mismatch")


def test_additional_submodule_config_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    register_agent_canon(root, metadata=GITMODULES + "\n[core]\n\tworktree = .\n")
    assert_finding(root, "agent-canon-submodule-config-mismatch")


def test_arbitrary_gitlink_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    register_agent_canon(root, path="vendor/other")
    assert_finding(root, "agent-canon-gitlink-set-mismatch")


def test_additional_gitlink_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    register_agent_canon(root)
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
    assert_finding(root, "agent-canon-gitlink-set-mismatch")


def test_initialized_checkout_matching_gitlink_passes(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    checkout = root / "vendor/agent-canon"
    checkout.mkdir(parents=True)
    run(["git", "init"], checkout)
    run(["git", "config", "user.email", "test@localhost"], checkout)
    run(["git", "config", "user.name", "Test"], checkout)
    (checkout / "README.md").write_text("source\n", encoding="utf-8")
    run(["git", "add", "README.md"], checkout)
    run(["git", "commit", "-m", "fixture"], checkout)
    pin = run(["git", "rev-parse", "HEAD"], checkout).stdout.strip()
    register_agent_canon(root, pin=pin)
    result = check(root)
    assert result.returncode == 0, result.stderr


def test_initialized_checkout_must_match_gitlink(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    register_agent_canon(root)
    checkout = root / "vendor/agent-canon"
    checkout.mkdir(parents=True)
    run(["git", "init"], checkout)
    run(["git", "config", "user.email", "test@localhost"], checkout)
    run(["git", "config", "user.name", "Test"], checkout)
    (checkout / "README.md").write_text("source\n", encoding="utf-8")
    run(["git", "add", "README.md"], checkout)
    run(["git", "commit", "-m", "fixture"], checkout)
    assert_finding(root, "agent-canon-checkout-pin-mismatch")


def test_uninitialized_checkout_directory_must_be_empty(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    register_agent_canon(root)
    checkout = root / "vendor/agent-canon"
    checkout.mkdir(parents=True)
    (checkout / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")
    assert_finding(root, "agent-canon-uninitialized-checkout-not-empty")


@pytest.mark.parametrize(
    ("path", "target"),
    [
        ("tools/agent-canon", "../vendor/agent-canon/tools"),
        ("notes/shared", "../vendor/agent-canon/notes"),
        ("tests/shared", "../vendor/agent-canon/tests"),
    ],
)
def test_agent_canon_runtime_symlinks_remain_rejected(
    tmp_path: Path, path: str, target: str
) -> None:
    root = make_fixture(tmp_path)
    link = root / path
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(target)
    run(["git", "add", path], root)
    result = check(root)
    assert result.returncode == 1
    assert "agent-canon" in result.stderr


def test_agent_canon_runtime_state_remains_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    state = root / ".agent-canon/state.toml"
    state.parent.mkdir()
    state.write_text("state = true\n", encoding="utf-8")
    run(["git", "add", ".agent-canon/state.toml"], root)
    assert_finding(root, "forbidden-tracked-path:.agent-canon")


def test_parent_agent_tools_test_namespace_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    test_path = root / "tests/agent_tools/test_runtime.py"
    test_path.parent.mkdir(parents=True)
    test_path.write_text("def test_runtime():\n    assert True\n", encoding="utf-8")
    run(["git", "add", str(test_path.relative_to(root))], root)
    assert_finding(root, "forbidden-tracked-path:tests/agent_tools")


def test_parent_static_seed_payload_fixture_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    fixture = root / "tests/fixtures/static-seed-c5fa3a22/payload.json"
    fixture.parent.mkdir(parents=True)
    fixture.write_text("{}\n", encoding="utf-8")
    run(["git", "add", str(fixture.relative_to(root))], root)
    assert_finding(root, "forbidden-tracked-path:tests/fixtures/static-seed-c5fa3a22")


def test_runtime_dispatch_reference_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    (root / "scripts/bootstrap.sh").write_text(
        "python3 agent_canon_source_root.py exec something\n", encoding="utf-8"
    )
    run(["git", "add", "scripts/bootstrap.sh"], root)
    assert_finding(root, "forbidden-runtime-reference:scripts/bootstrap.sh")


def test_legacy_submodule_strategy_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    (root / "scripts/bootstrap.sh").write_text(
        "submodule_strategy=github_submodule\n", encoding="utf-8"
    )
    run(["git", "add", "scripts/bootstrap.sh"], root)
    assert_finding(root, "forbidden-runtime-reference:scripts/bootstrap.sh")


def test_seed_registration_requires_regular_file(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    (root / ".codex/agents/worker.toml").unlink()
    (root / ".codex/agents/worker.toml").symlink_to("missing.toml")
    run(["git", "add", ".codex/agents/worker.toml"], root)
    assert_finding(root, "static-seed-agent-file-not-regular")
