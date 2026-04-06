# Agent Instructions

This repository keeps human-maintained agent canon under `agents/`.
Use this file as the runtime entrypoint for Codex and GitHub Copilot agents.

## Read First

- `README.md`
- `documents/WORKFLOW_GUIDE.md`
- `agents/README.md`
- `agents/canonical/README.md`
- `agents/canonical/CODEX_WORKFLOW.md`
- `agents/skills/README.md`
- `documents/AGENTS_COORDINATION.md`
- `docker/README.md`

## Repo Defaults

- Human-facing primary language is Japanese.
- The repository default integration branch is `main`.
- This template assumes Python implementation and Markdown documentation are both first-class.
- Long-lived rules belong in `documents/`.
- Durable notes and research summaries belong in `notes/`.
- Shared development environment guidance belongs in `docker/`.

## Agent Canon

- Human hub: `agents/README.md`
- Shared canonical layout: `agents/canonical/README.md`
- Team definition: `agents/agents_config.json`
- Workflow catalog: `agents/TASK_WORKFLOWS.md`
- Communication protocol: `agents/COMMUNICATION_PROTOCOL.md`
- Machine-readable task catalog: `agents/task_catalog.yaml`
- Artifact placement: `agents/canonical/ARTIFACT_PLACEMENT.md`
- CLI entrypoints: `agents/canonical/CLI_ENTRYPOINTS.md`
- Codex subagents: `agents/canonical/CODEX_SUBAGENTS.md`
- Human skill canon: `agents/skills/README.md`
- Human skill catalog: `agents/skills/catalog.yaml`
- Workflow references: `documents/workflow-references.md`

## Skills

- Canonical project skills for Codex/Copilot agent mode live in `.agents/skills/`.
- Claude-compatible mirrors live in `.claude/skills/` and are synced from `.agents/skills/`.

## Codex Runtime

- Project-scoped Codex config lives in `.codex/`.
- Codex subagent definitions live in `.codex/agents/*.toml`.

## Codex Default Flow

1. Read `agents/canonical/CODEX_WORKFLOW.md`.
1. Pick one workflow family from `agents/TASK_WORKFLOWS.md`.
1. Pick the minimal skill set from `agents/skills/README.md`.
1. Use `agents/canonical/ARTIFACT_PLACEMENT.md` before creating new task documents.
1. Load only the skills needed for the task from `.agents/skills/`.
1. If handoff, specialist delegation, or review artifacts matter, check `agents/canonical/CODEX_SUBAGENTS.md` and bootstrap `reports/agents/<run-id>/`.
1. Validate with `make ci-quick`, then broader checks if the change warrants them.
1. If the task changed repo files and the user did not explicitly forbid it, commit and push the branch before the final completion report.

## Research Defaults

- Literature-heavy tasks should normally use `literature-survey`.
- Research-driven tasks should normally use `research-workflow` as the outer loop.
- Single-run experiment execution and rerun branching should normally use `experiment-lifecycle`.
- Benchmark-driven code changes that should keep iterating until an explicit decision state should add `experiment-change-loop`.
- Claim-heavy experiment work should normally pass both `critical-review` and `report-review`.
- If methodology, benchmark protocol, artifact policy, or reporting policy changes substantially, add `research-perspective-review`.

## Python And Markdown Baseline

- Python changes should normally pass `pyright`, `pytest python/tests/`, and `ruff check python/ --select D,E,F,I,UP`.
- Dependency-sensitive changes should normally inspect `pipdeptree --warn fail` and `deptry python`.
- Markdown-heavy changes should normally pass `make docs-check`.

## Validation Commands

    make agent-checks
    make ci-quick
    make ci
    make docs-check
    bash scripts/run_comprehensive_review.sh

## Environment Notes

- If you touch Python dependencies, update `docker/Dockerfile` and `docker/requirements.txt` together.
- Repo-wide tool introduction proposals should follow `environment-maintenance` and `agents/templates/environment_change_proposal.md`.
- Container runtime selection should follow `docker/packs/*.toml`, `docker/codex-container-profiles.toml`, and `docker/python-execution-rules.toml`.
- Worktree kickoff and scope refresh should use `worktree-start`; drift and cleanup checks should use `worktree-health`.
- Final completion reports should normally be sent only after commit and push are done. If push is blocked or intentionally skipped, state that explicitly in the report.
- Prefer repository docs and checked-in scripts over agent-specific guesses.
- Keep runtime entrypoint files thin; update the canonical docs in `agents/` first.
- If workflow or review policy changes are based on external sources, update `documents/workflow-references.md`.
