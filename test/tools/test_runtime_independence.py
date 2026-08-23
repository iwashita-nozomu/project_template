"""Focused tests for the source-free AgentCanon boundary."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKER = REPO_ROOT / "tools/check_runtime_independence.py"


def run(
    args: list[str], cwd: Path, *, check: bool = True
) -> subprocess.CompletedProcess[str]:
    """Run a fixture command and capture its output."""
    return subprocess.run(args, cwd=cwd, check=check, capture_output=True, text=True)


def make_fixture(tmp_path: Path) -> Path:
    """Create a minimal committed source-free template fixture."""
    root = tmp_path / "fixture"
    (root / "tools").mkdir(parents=True)
    (root / "scripts").mkdir()
    shutil.copy2(CHECKER, root / "tools/check_runtime_independence.py")
    (root / "AGENTS.md").write_text(
        "Optional AgentCanon development notes are documentation only.\n",
        encoding="utf-8",
    )
    run(["git", "init"], root)
    run(["git", "config", "user.email", "test@localhost"], root)
    run(["git", "config", "user.name", "Test"], root)
    run(["git", "add", "--all"], root)
    run(["git", "commit", "-m", "fixture"], root)
    return root


def check(root: Path) -> subprocess.CompletedProcess[str]:
    """Run the independence checker against a fixture."""
    return run(
        ["python3", "tools/check_runtime_independence.py", "--root", str(root)],
        root,
        check=False,
    )


def add_and_commit(root: Path, relative: str, content: str) -> None:
    """Add a fixture file and commit it to the fixture index."""
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    run(["git", "add", relative], root)
    run(["git", "commit", "-m", "fixture mutation"], root)


def test_clean_source_free_tree_passes(tmp_path: Path) -> None:
    """Accept a clean tree with no AgentCanon integration surface."""
    result = check(make_fixture(tmp_path))
    assert result.returncode == 0, result.stderr
    assert "RUNTIME_INDEPENDENCE=pass" in result.stdout


def test_agent_canon_submodule_metadata_is_rejected(tmp_path: Path) -> None:
    """Reject only metadata that registers an AgentCanon checkout."""
    root = make_fixture(tmp_path)
    (root / ".gitmodules").write_text(
        '[submodule "vendor/agent-canon"]\n'
        "\tpath = vendor/agent-canon\n"
        "\turl = https://github.com/iwashita-nozomu/agent-canon.git\n",
        encoding="utf-8",
    )
    run(["git", "add", ".gitmodules"], root)
    result = check(root)
    assert result.returncode == 1
    assert "agent-canon-submodule-forbidden:.gitmodules" in result.stderr


def test_unrelated_submodule_and_gitlink_are_allowed(tmp_path: Path) -> None:
    """Do not turn the AgentCanon boundary into a generic submodule ban."""
    root = make_fixture(tmp_path)
    (root / ".gitmodules").write_text(
        '[submodule "vendor/other"]\n'
        "\tpath = vendor/other\n"
        "\turl = https://example.invalid/other.git\n",
        encoding="utf-8",
    )
    run(["git", "add", ".gitmodules"], root)
    run(
        [
            "git",
            "update-index",
            "--add",
            "--cacheinfo",
            f"160000,{('1' * 40)},vendor/other",
        ],
        root,
    )
    result = check(root)
    assert result.returncode == 0, result.stderr
    assert "RUNTIME_INDEPENDENCE=pass" in result.stdout


def test_agent_canon_source_symlink_is_rejected(tmp_path: Path) -> None:
    """Reject a symlink whose target exposes an AgentCanon source checkout."""
    root = make_fixture(tmp_path)
    (root / "scripts/canon-runtime").symlink_to(
        "../workspace/agent-canondevelop/task/agent-canon"
    )
    run(["git", "add", "scripts/canon-runtime"], root)
    result = check(root)
    assert result.returncode == 1
    assert "agent-canon-source-symlink:scripts/canon-runtime" in result.stderr


def test_agent_canon_named_symlink_is_rejected_even_when_target_is_generic(
    tmp_path: Path,
) -> None:
    """Reject a symlink named for AgentCanon even with a generic target."""
    root = make_fixture(tmp_path)
    (root / "scripts/agent-canon").symlink_to("../scripts/start_repository.sh")
    run(["git", "add", "scripts/agent-canon"], root)
    result = check(root)
    assert result.returncode == 1
    assert "agent-canon-source-symlink:scripts/agent-canon" in result.stderr


def test_static_seed_and_source_resolver_paths_are_rejected(tmp_path: Path) -> None:
    """Reject tracked static-seed artifacts by path."""
    root = make_fixture(tmp_path)
    (root / "documents/design").mkdir(parents=True)
    path = root / "documents/design/agent-canon-static-seed-import.md"
    path.write_text("retired\n", encoding="utf-8")
    run(["git", "add", str(path.relative_to(root))], root)
    result = check(root)
    assert result.returncode == 1
    assert "forbidden-source-artifact:" in result.stderr


def test_source_resolver_artifact_is_rejected_by_path(tmp_path: Path) -> None:
    """Reject a source resolver artifact outside normal execution paths."""
    root = make_fixture(tmp_path)
    path = root / "tools/agent_canon_source_root.py"
    path.write_text("raise SystemExit(0)\n", encoding="utf-8")
    run(["git", "add", str(path.relative_to(root))], root)
    result = check(root)
    assert result.returncode == 1
    assert "forbidden-source-artifact:tools/agent_canon_source_root.py" in result.stderr


def test_execution_source_resolver_reference_is_rejected(tmp_path: Path) -> None:
    """Reject a source resolver reference in an executable script."""
    root = make_fixture(tmp_path)
    add_and_commit(
        root,
        "scripts/bootstrap.sh",
        "python3 agent_canon_source_root.py exec\n",
    )
    result = check(root)
    assert result.returncode == 1
    assert "forbidden-runtime-reference:scripts/bootstrap.sh:agent_canon_source" in result.stderr


def test_execution_vendor_reference_is_rejected(tmp_path: Path) -> None:
    """Reject a vendored AgentCanon path in a Docker execution script."""
    root = make_fixture(tmp_path)
    add_and_commit(root, "docker/run.sh", "cd vendor/agent-canon\n")
    result = check(root)
    assert result.returncode == 1
    assert "forbidden-runtime-reference:docker/run.sh:vendor/agent-canon" in result.stderr


def test_test_entry_vendor_reference_is_rejected(tmp_path: Path) -> None:
    """The executable test list cannot restore an AgentCanon source dependency."""
    root = make_fixture(tmp_path)
    add_and_commit(
        root,
        "test/testlist.toml",
        'command = ["python3", "vendor/agent-canon/tool.py"]\n',
    )
    result = check(root)
    assert result.returncode == 1
    assert "forbidden-runtime-reference:test/testlist.toml:vendor/agent-canon" in result.stderr


def test_documentation_and_ignored_development_workspace_are_not_runtime_dependencies(
    tmp_path: Path,
) -> None:
    """Allow optional development prose and ignored workspace content."""
    root = make_fixture(tmp_path)
    (root / "documents").mkdir(exist_ok=True)
    (root / "documents/notes.md").write_text(
        "Edit AgentCanon only in workspace/agent-canondevelop.\n", encoding="utf-8"
    )
    (root / "workspace/agent-canondevelop/task/agent-canon").mkdir(parents=True)
    result = check(root)
    assert result.returncode == 0, result.stderr
