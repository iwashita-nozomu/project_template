"""Guard the root README consumer/maintainer boundary for static configuration."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
README = PROJECT_ROOT / "README.md"
MAINTENANCE_CONTRACT = "documents/design/template-static-seed-import.md"


def test_root_readme_keeps_static_configuration_consumer_facing() -> None:
    """Keep producer provenance and import operations out of normal user guidance."""
    text = README.read_text(encoding="utf-8")
    lowered = text.lower()

    for token in (
        "agentcanon",
        "agent-canon",
        "agent-canon-static-seed.json",
        "producer repository",
        "producer tooling",
        "producer revision",
        "newer producer",
        "import_agent_canon_static_seed",
        "<fresh-export-directory>",
    ):
        assert token not in lowered

    normalized = " ".join(text.split())
    for clause in (
        ".codex/config.toml",
        ".codex/agents/*.toml",
        "regular tracked files",
        "exact role-file closure",
        "background refresh",
        "normal users do not run it",
    ):
        assert clause in normalized

    assert f"]({MAINTENANCE_CONTRACT})" in text
    assert (PROJECT_ROOT / MAINTENANCE_CONTRACT).is_file()
