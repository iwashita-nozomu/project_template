# @dependency-start
# responsibility Defines deterministic template experiment cases.
# upstream design ../../vendor/agent-canon/documents/experiment-registry.md defines managed experiment expectations.
# downstream implementation experimentcode.py evaluates these cases.
# @dependency-end
"""Minimal case definitions for one experiment topic."""

from __future__ import annotations

from dataclasses import dataclass

DEFAULT_CASE_LIMIT = 8
CASE_ID_WIDTH = 3


@dataclass(frozen=True)
class ExperimentCase:
    """One case for the template experiment."""

    case_id: str
    value: int


def build_cases(limit: int = DEFAULT_CASE_LIMIT) -> list[ExperimentCase]:
    """Build a small deterministic case list."""
    return [
        ExperimentCase(case_id=f"case_{index:0{CASE_ID_WIDTH}d}", value=index)
        for index in range(limit)
    ]
