"""Verify generated outputs stay outside the tracked repository structure."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def ignore_root(tmp_path: Path) -> Path:
    """Use a temporary Git index so review checks never mutate the real index."""
    root = tmp_path / "root"
    root.mkdir()
    (root / ".gitignore").write_bytes(
        (PROJECT_ROOT / ".gitignore").read_bytes()
    )
    subprocess.run(["git", "init", "--quiet"], cwd=root, check=True)
    return root


def _matching_rule(relative: str, ignore_root: Path) -> tuple[str, str] | None:
    """Return the matching ignore owner and pattern for one candidate path."""
    result = subprocess.run(
        ["git", "check-ignore", "-v", "--no-index", "--", relative],
        cwd=ignore_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 1:
        return None
    assert result.returncode == 0, result.stderr
    rule, matched = result.stdout.rstrip("\n").split("\t", 1)
    owner, _line, pattern = rule.rsplit(":", 2)
    assert matched == relative
    return owner, pattern


def test_generated_outputs_are_root_ignored(ignore_root: Path) -> None:
    """One root policy owns repository-level generated output trees."""
    for relative in (
        "build/dev/CMakeCache.txt",
        "dist/project.whl",
        ".state/install/dev/lib/libproject-core.a",
        "logs/runtime.log",
        "reports/coverage.html",
        "test/logs/pytest.log",
        "experiments/topic/result/run-1/summary.json",
        "workspace/task/output.txt",
    ):
        assert _matching_rule(relative, ignore_root) is not None


def test_nested_same_name_directories_are_not_hidden(ignore_root: Path) -> None:
    """Root-anchored output rules do not hide product-owned nested paths."""
    for relative in (
        "src/build/model.cpp",
        "documents/reports/design.md",
        "tools/logs/diagnostic.log",
    ):
        assert _matching_rule(relative, ignore_root) is None


def test_generated_output_directories_are_not_tracked() -> None:
    """Generated roots do not need placeholder or local-policy files."""
    for relative in (
        "build/.gitignore",
        "dist/.gitignore",
        ".state/.gitignore",
        "logs/.gitignore",
        "reports/.gitignore",
    ):
        assert not (PROJECT_ROOT / relative).exists()
