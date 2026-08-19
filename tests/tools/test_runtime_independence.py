"""Focused tests for the exact AgentCanon registration and live Codex view."""

from __future__ import annotations

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
LIVE_VIEWS = {
    "AGENTS.md": "vendor/agent-canon/ROOT_AGENTS.md",
    ".codex/config.toml": "../vendor/agent-canon/.codex/config.toml",
    ".codex/agents": "../vendor/agent-canon/.codex/agents",
    ".codex/hooks.json": "../vendor/agent-canon/.codex/hooks.json",
    ".codex/hooks": "../vendor/agent-canon/.codex/hooks",
}


def run(args: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=check, capture_output=True, text=True)


def make_fixture(tmp_path: Path) -> Path:
    root = tmp_path / "fixture"
    (root / "tools").mkdir(parents=True)
    (root / ".codex").mkdir()
    (root / "scripts").mkdir()
    shutil.copy2(CHECKER, root / "tools/check_runtime_independence.py")
    (root / "Makefile").write_text("check:\n\t@true\n", encoding="utf-8")
    (root / ".gitmodules").write_text(GITMODULES, encoding="utf-8")
    for relative, target in LIVE_VIEWS.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(target)

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


def replace_symlink(root: Path, relative: str, target: str) -> None:
    path = root / relative
    path.unlink()
    path.symlink_to(target)
    run(["git", "add", relative], root)


def test_exact_uninitialized_live_projection_passes(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    result = check(root)
    assert result.returncode == 0, result.stderr
    assert "RUNTIME_INDEPENDENCE=pass" in result.stdout
    for relative, target in LIVE_VIEWS.items():
        entry = run(["git", "ls-files", "-s", relative], root).stdout
        assert entry.startswith("120000 ")
        assert (root / relative).readlink().as_posix() == target
    checkout = root / "vendor/agent-canon"
    assert not checkout.exists()


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


def test_initialized_checkout_at_exact_pin_passes(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    checkout = root / "vendor/agent-canon"
    checkout.mkdir(parents=True)
    run(["git", "init"], checkout)
    run(["git", "config", "user.email", "test@localhost"], checkout)
    run(["git", "config", "user.name", "Test"], checkout)
    (checkout / "README.md").write_text("source\n", encoding="utf-8")
    run(["git", "add", "README.md"], checkout)
    run(["git", "commit", "-m", "fixture"], checkout)
    head = run(["git", "rev-parse", "HEAD"], checkout).stdout.strip()
    run(
        [
            "git",
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{head},vendor/agent-canon",
        ],
        root,
    )
    result = check(root)
    assert result.returncode == 0, result.stderr


def test_uninitialized_checkout_directory_must_be_empty(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    checkout = root / "vendor/agent-canon"
    checkout.mkdir(parents=True)
    (checkout / "unexpected.txt").write_text("unexpected\n", encoding="utf-8")
    result = check(root)
    assert result.returncode == 1
    assert "agent-canon-uninitialized-checkout-not-empty" in result.stderr


def test_missing_required_live_view_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    (root / ".codex/hooks.json").unlink()
    run(["git", "add", "-u", ".codex/hooks.json"], root)
    result = check(root)
    assert result.returncode == 1
    assert "required-live-view-missing:.codex/hooks.json" in result.stderr


def test_regular_copy_cannot_replace_live_view(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    path = root / ".codex/config.toml"
    path.unlink()
    path.write_text('model = "copied"\n', encoding="utf-8")
    run(["git", "add", ".codex/config.toml"], root)
    result = check(root)
    assert result.returncode == 1
    assert "required-live-view-not-symlink:.codex/config.toml:100644" in result.stderr


def test_wrong_live_view_target_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    replace_symlink(
        root,
        ".codex/agents",
        "../vendor/agent-canon/copied-agents",
    )
    result = check(root)
    assert result.returncode == 1
    assert "required-live-view-target-mismatch:.codex/agents" in result.stderr


def test_copied_agent_definitions_are_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    path = root / ".codex/agents"
    path.unlink()
    path.mkdir()
    (path / "worker.toml").write_text('name = "worker"\n', encoding="utf-8")
    run(["git", "add", "-A", ".codex/agents"], root)
    result = check(root)
    assert result.returncode == 1
    assert "copied-agent-definition:.codex/agents/worker.toml" in result.stderr


def test_tools_alias_remains_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    (root / "tools/agent-canon").symlink_to("../vendor/agent-canon/tools")
    run(["git", "add", "tools/agent-canon"], root)
    result = check(root)
    assert result.returncode == 1
    assert "forbidden-tracked-path:tools/agent-canon" in result.stderr


def test_unmanaged_agent_canon_symlink_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    (root / "scripts/canon").symlink_to("../vendor/agent-canon/tools")
    run(["git", "add", "scripts/canon"], root)
    result = check(root)
    assert result.returncode == 1
    assert "unmanaged-agent-canon-symlink:scripts/canon" in result.stderr


def test_parent_agent_tools_test_namespace_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    test_path = root / "tests/agent_tools/test_runtime.py"
    test_path.parent.mkdir(parents=True)
    test_path.write_text("def test_runtime():\n    assert True\n", encoding="utf-8")
    run(["git", "add", str(test_path.relative_to(root))], root)
    result = check(root)
    assert result.returncode == 1
    assert "forbidden-tracked-path:tests/agent_tools" in result.stderr


def test_parent_static_seed_payload_fixture_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    fixture = root / "tests/fixtures/static-seed-c5fa3a22/payload.json"
    fixture.parent.mkdir(parents=True)
    fixture.write_text("{}\n", encoding="utf-8")
    run(["git", "add", str(fixture.relative_to(root))], root)
    result = check(root)
    assert result.returncode == 1
    assert "forbidden-tracked-path:tests/fixtures/static-seed-c5fa3a22" in result.stderr


def test_static_seed_provenance_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    (root / "agent-canon-static-seed.json").write_text("{}\n", encoding="utf-8")
    run(["git", "add", "agent-canon-static-seed.json"], root)
    result = check(root)
    assert result.returncode == 1
    assert "forbidden-tracked-path:agent-canon-static-seed.json" in result.stderr


def test_static_seed_importer_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    importer = root / "tools/import_agent_canon_static_seed.py"
    importer.write_text("raise SystemExit(0)\n", encoding="utf-8")
    run(["git", "add", "tools/import_agent_canon_static_seed.py"], root)
    result = check(root)
    assert result.returncode == 1
    assert "forbidden-tracked-path:tools/import_agent_canon_static_seed.py" in result.stderr


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
