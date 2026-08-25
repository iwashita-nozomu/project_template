from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "AGENTS.md"
SPECIFIC = ROOT / "documents/agent-canon/consumer-root-instructions.md"


def _section(data: bytes, start: bytes, end: bytes) -> bytes:
    start_index = data.index(start) + len(start)
    end_index = data.index(end, start_index)
    return data[start_index:end_index]


def test_consumer_agents_is_composed_regular_file_with_specific_tail() -> None:
    assert OUTPUT.exists()
    assert OUTPUT.is_file()
    assert not OUTPUT.is_symlink()
    assert SPECIFIC.is_file()
    assert not SPECIFIC.is_symlink()
    assert not (ROOT / "AGENT.md").exists()

    output = OUTPUT.read_bytes()
    specific = SPECIFIC.read_bytes()
    base_start = b"<!-- agent-canon:consumer-root-base:start -->\n"
    base_end = b"<!-- agent-canon:consumer-root-base:end -->\n"
    specific_start = b"<!-- agent-canon:consumer-root-specific:start -->\n"
    specific_end = b"<!-- agent-canon:consumer-root-specific:end -->\n"

    assert output.startswith(b"<!-- agent-canon:consumer-root-agents:v1 -->\n")
    assert output.index(base_start) < output.index(specific_start)
    assert _section(output, specific_start, specific_end) == specific + b"\n"
    assert _section(output, base_start, base_end)
    assert b"source-commit=" in output


def test_project_specific_clauses_are_not_lost_from_composition() -> None:
    output = OUTPUT.read_bytes()
    specific = SPECIFIC.read_bytes()
    unique_clauses = (
        b"generated project's source, build, tests, Docker",
        b"test/testrunner.sh",
        b"without hidden external repository state",
        b"self-contained and usable without an",
    )
    for clause in unique_clauses:
        assert clause in specific
        assert clause in output
