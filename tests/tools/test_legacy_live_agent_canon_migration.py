"""Focused contract tests for pre-#168 live AgentCanon descendants."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION = REPO_ROOT / "documents/contracts/legacy-live-agent-canon-migration.md"
DOCUMENT_INDEX = REPO_ROOT / "documents/README.md"


def migration_text() -> str:
    return MIGRATION.read_text(encoding="utf-8")


def test_migration_contract_is_reachable_from_documents_index() -> None:
    index = DOCUMENT_INDEX.read_text(encoding="utf-8")
    assert (
        "[Legacy live AgentCanon descendant migration]"
        "(contracts/legacy-live-agent-canon-migration.md)"
    ) in index


def test_current_template_remains_static_seed_and_runtime_independent() -> None:
    text = migration_text()
    assert "Current Template descendants are different" in text
    assert "audited static seed as regular files" in text
    assert "must not be added to the current default path" in text
    assert "This Template does not own or duplicate that state machine" in text


def test_legacy_route_forbids_bypassing_publication_identity() -> None:
    text = migration_text()
    required_prohibitions = (
        "manually fast-forwarding or staging the `vendor/agent-canon` gitlink",
        "copying transaction markers, QueueReceipts, DependencyFrontiers, or G4 receipts",
        "adding a second updater, compatibility state machine, background updater",
        "do not replace the repository tree with the current Template tree",
    )
    for prohibition in required_prohibitions:
        assert prohibition in text


def test_migration_separates_bounded_live_update_from_permanent_removal() -> None:
    text = migration_text()
    assert "### Route A: temporarily retain the live runtime" in text
    assert "### Route B: migrate permanently to the static-seed contract" in text
    assert "source-publication-ready.json" in text
    assert "mode-`160000` gitlink" in text
    assert "Verify a source-free clone" in text
    assert "AgentCanon issue [#724]" in text
