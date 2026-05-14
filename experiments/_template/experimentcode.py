# @dependency-start
# responsibility Runs the template managed experiment entrypoint.
# upstream design ../../vendor/agent-canon/documents/experiment-registry.md defines managed experiment command protocol.
# upstream implementation ../registry.toml registers smoke and formal commands for this entrypoint.
# upstream implementation ../../tools/experiments/run_managed_experiment.py exports config_path before command execution.
# downstream implementation result stores per-run JSON and JSONL outputs.
# @dependency-end
"""Minimal experiment entrypoint that writes JSON/JSONL outputs."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from cases import ExperimentCase
from cases import build_cases

DEFAULT_CASE_LIMIT = 8
MILLISECONDS_PER_SECOND = 1000.0


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Run the template experiment and write canonical outputs."
    )
    parser.add_argument(
        "--run-dir",
        required=True,
        help="Directory where summary.json, cases.jsonl, and logs for this run go.",
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Managed-run config JSON exported by run_managed_experiment.py.",
    )
    parser.add_argument(
        "--mode",
        choices=("smoke", "formal"),
        default="smoke",
        help="Registered run mode label.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_CASE_LIMIT,
        help="Number of synthetic cases to execute.",
    )
    parser.add_argument(
        "--sleep-ms",
        type=float,
        default=0.0,
        help="Optional sleep per case to emulate a longer run.",
    )
    return parser.parse_args()


def load_config(config_path: str) -> dict[str, object]:
    """Load managed-run configuration."""
    data = json.loads(Path(config_path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("managed-run config must be a JSON object")
    return data


def evaluate_case(case: ExperimentCase, sleep_ms: float) -> dict[str, object]:
    """Run one synthetic case."""
    if sleep_ms > 0:
        time.sleep(sleep_ms / MILLISECONDS_PER_SECOND)

    score = float(case.value * case.value)
    return {
        "case_id": case.case_id,
        "status": "ok",
        "value": case.value,
        "score": score,
    }


def main() -> int:
    """Run the template experiment."""
    args = parse_args()
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    config = load_config(args.config)

    results = [evaluate_case(case, args.sleep_ms) for case in build_cases(args.limit)]
    cases_path = run_dir / "cases.jsonl"
    with cases_path.open("w", encoding="utf-8") as handle:
        for record in results:
            handle.write(json.dumps(record, ensure_ascii=True))
            handle.write("\n")

    ok_scores = [float(record["score"]) for record in results if record["status"] == "ok"]
    summary = {
        "case_count": len(results),
        "success_count": len(ok_scores),
        "failure_count": len(results) - len(ok_scores),
        "mean_score": sum(ok_scores) / len(ok_scores) if ok_scores else None,
        "mode": args.mode,
        "config_topic": config.get("topic"),
        "status": "completed",
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
