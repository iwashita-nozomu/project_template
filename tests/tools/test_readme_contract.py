"""Guard the parent README and self-contained project test workflow."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
README = PROJECT_ROOT / "README.md"


def test_root_readme_describes_source_free_project_boundary() -> None:
    text = README.read_text(encoding="utf-8")
    lowered = text.lower()

    for forbidden in (
        "vendor/agent-canon",
        ".gitmodules",
        "git submodule update",
        ".codex/config.toml",
    ):
        assert forbidden not in lowered

    normalized = " ".join(text.split())
    for required in (
        "source-free with respect to AgentCanon",
        "project Docker images",
        "workspace/agent-canondevelop",
        "docker build -f docker/Dockerfile -t project-template .",
        "docker run --rm project-template test/testrunner.sh",
        "test/testlist.toml",
        "no workspace mount",
    ):
        assert required in normalized


def test_parent_test_entrypoints_are_tracked_and_executable() -> None:
    runner = PROJECT_ROOT / "test/testrunner.sh"
    test_list = PROJECT_ROOT / "test/testlist.toml"
    assert runner.is_file()
    assert runner.stat().st_mode & 0o111
    assert test_list.is_file()
