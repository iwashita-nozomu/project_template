"""Verify that ignore rules live with the responsibility that creates artifacts."""

from __future__ import annotations

import subprocess
import shutil
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
IGNORE_ROOT: Path | None = None


@pytest.fixture(scope="module", autouse=True)
def isolated_ignore_repository(tmp_path_factory: pytest.TempPathFactory) -> None:
    """Provide Git ignore semantics without requiring the source checkout's .git."""
    global IGNORE_ROOT
    root = tmp_path_factory.mktemp("gitignore-fixture")
    for relative in (
        ".gitignore",
        "build/.gitignore",
        ".state/.gitignore",
        "dist/.gitignore",
        "logs/.gitignore",
        "reports/.gitignore",
        "tests/.gitignore",
        "experiments/.gitignore",
        "experiments/topic/result/.gitignore",
    ):
        source = PROJECT_ROOT / relative
        if source.is_file():
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    subprocess.run(["git", "init", "--quiet", str(root)], check=True)
    IGNORE_ROOT = root


def _matching_rule(path: str) -> tuple[str, str] | None:
    """Return the matching ignore owner and pattern for a repository-relative path."""
    assert IGNORE_ROOT is not None
    result = subprocess.run(
        ["git", "check-ignore", "-v", "--no-index", "--", path],
        cwd=IGNORE_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 1:
        assert result.stdout == ""
        return None
    assert result.returncode == 0, result.stderr

    rule, matched_path = result.stdout.rstrip("\n").split("\t", 1)
    source, _line, pattern = rule.rsplit(":", 2)
    assert matched_path == path
    return source, pattern


def _assert_ignored_by(path: str, owner: str) -> None:
    """Assert that a path is ignored by the expected non-negated rule owner."""
    match = _matching_rule(path)
    assert match is not None
    source, pattern = match
    assert source == owner
    assert not pattern.startswith("!")


def _assert_visible(path: str) -> None:
    """Assert that a path is either unmatched or restored by a negated rule."""
    match = _matching_rule(path)
    assert match is None or match[1].startswith("!")


def test_generated_outputs_are_ignored_by_local_owner() -> None:
    """Resolve generated outputs to the nearest lifecycle owner."""
    cases = {
        "build/cpp/dev/CMakeCache.txt": "build/.gitignore",
        ".state/cpp-install/dev/bin/example": ".state/.gitignore",
        "dist/project_template-0.1.0-py3-none-any.whl": "dist/.gitignore",
        "logs/runtime.log": "logs/.gitignore",
        "reports/coverage.html": "reports/.gitignore",
        "tests/logs/pytest.log": "tests/.gitignore",
        "experiments/topic/result/run-001/summary.json": "experiments/.gitignore",
    }
    for path, owner in cases.items():
        _assert_ignored_by(path, owner)


def test_cross_tree_artifacts_remain_root_owned() -> None:
    """Keep genuinely cross-cutting artifacts in the root policy."""
    for path in (
        "tests/tools/__pycache__/test_gitignore_layout.cpython-311.pyc",
        "python/project_template.egg-info/PKG-INFO",
        "experiments/topic/notebooks/.ipynb_checkpoints/plot-checkpoint.ipynb",
        "documents/.DS_Store",
        ".worktrees/issue-177/index.lock",
        "workspace/scratch/output.txt",
    ):
        _assert_ignored_by(path, ".gitignore")


def test_placeholders_owner_files_and_noncanonical_directories_stay_visible() -> None:
    """Do not hide tracked policy files, placeholders, or unrelated same-name trees."""
    for path in (
        "build/.gitignore",
        ".state/.gitignore",
        "dist/.gitignore",
        "logs/.gitignore",
        "reports/.gitignore",
        "experiments/topic/result/.gitkeep",
        "cpp/build/generated-object.o",
        "tools/logs/diagnostic.log",
        "documents/reports/design.md",
    ):
        _assert_visible(path)


def test_root_policy_does_not_duplicate_local_output_ownership() -> None:
    """Keep local output policies out of the root ignore file."""
    patterns = {
        line.strip()
        for line in (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    assert patterns.isdisjoint(
        {
            "build/",
            "dist/",
            ".state/",
            "logs/",
            "tests/logs/",
            "reports/",
            "experiments/**/result/*",
            "!experiments/**/result/.gitkeep",
        }
    )
