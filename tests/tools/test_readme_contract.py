"""Guard the root README ownership and AgentCanon activation boundary."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
README = PROJECT_ROOT / "README.md"


def test_root_readme_describes_exact_live_view_without_static_copy() -> None:
    text = README.read_text(encoding="utf-8")
    lowered = text.lower()

    for token in (
        "agent-canon-static-seed.json",
        "import_agent_canon_static_seed",
        "template-static-seed-import",
        "regular tracked files under `.codex`",
        "background refresh",
    ):
        assert token not in lowered

    normalized = " ".join(text.split())
    for clause in (
        "one exact AgentCanon submodule pin",
        "Normal project checks",
        "without initializing the checkout",
        "git submodule update --init --checkout -- vendor/agent-canon",
        "AGENTS.md",
        ".codex/config.toml",
        ".codex/agents",
        ".codex/hooks.json",
        ".codex/hooks",
        "Agent definitions",
        "remain owned by AgentCanon",
        "does not copy those files",
        "do not run it automatically",
        "tools/agent-canon",
    ):
        assert clause in normalized


def test_root_readme_live_view_matches_tracked_symlinks() -> None:
    expected = {
        "AGENTS.md": "vendor/agent-canon/ROOT_AGENTS.md",
        ".codex/config.toml": "../vendor/agent-canon/.codex/config.toml",
        ".codex/agents": "../vendor/agent-canon/.codex/agents",
        ".codex/hooks.json": "../vendor/agent-canon/.codex/hooks.json",
        ".codex/hooks": "../vendor/agent-canon/.codex/hooks",
    }
    for relative, target in expected.items():
        path = PROJECT_ROOT / relative
        assert path.is_symlink()
        assert path.readlink().as_posix() == target
