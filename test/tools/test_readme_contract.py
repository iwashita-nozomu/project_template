"""Guard the parent README and self-contained project test workflow."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
README = PROJECT_ROOT / "README.md"


def test_root_readme_describes_source_free_project_boundary() -> None:
    """README exposes the source-free project and canonical test route."""
    text = README.read_text(encoding="utf-8")
    lowered = text.lower()

    for forbidden in (".gitmodules", "git submodule update", ".codex/config.toml"):
        assert forbidden not in lowered

    normalized = " ".join(text.split())
    for required in (
            "project development",
        "project Docker images",
        "bash docker/run-tests.sh --tag project-template:test",
        "test/testlist.toml",
        "no workspace mount",
    ):
        assert required in normalized


def test_parent_test_entrypoints_are_tracked_and_executable() -> None:
    """The single runner and list are present and executable where required."""
    runner = PROJECT_ROOT / "test/testrunner.sh"
    test_list = PROJECT_ROOT / "test/testlist.toml"
    assert runner.is_file()
    assert runner.stat().st_mode & 0o111
    assert test_list.is_file()


def test_root_layout_has_one_source_test_and_experiment_owner() -> None:
    """The reader-facing layout matches the executable repository structure."""
    assert (PROJECT_ROOT / "CMakeLists.txt").is_file()
    assert (PROJECT_ROOT / "CMakePresets.json").is_file()
    assert (PROJECT_ROOT / "include/project/version.hpp").is_file()
    assert (PROJECT_ROOT / "src/version.cpp").is_file()
    assert (PROJECT_ROOT / "test/cpp/version_test.cpp").is_file()
    assert not (PROJECT_ROOT / "cpp").exists()
    assert not (PROJECT_ROOT / "tests").exists()
    assert not (PROJECT_ROOT / "Makefile").exists()
