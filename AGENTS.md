# Agent Instructions

This repository keeps human-maintained agent canon under `agents/`.
Use this file as the runtime entrypoint for Codex and GitHub Copilot agents.

## Read First

- `README.md`
- `agents/README.md`
- `agents/canonical/README.md`
- `agents/canonical/CODEX_WORKFLOW.md`
- `agents/skills/README.md`
- `documents/AGENTS_COORDINATION.md`

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

## Skills

- Canonical project skills for Codex/Copilot agent mode live in `.agents/skills/`.
- Claude-compatible mirrors live in `.claude/skills/`.

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

## Python And Markdown Baseline

- Python changes should normally pass `pyright python/`, `pytest python/tests/`, and `ruff check python/ --select D,E,F,I,UP`.
- Dependency-sensitive changes should normally inspect `pipdeptree --warn fail` and `deptry python`.
- Markdown-heavy changes should normally pass `python3 scripts/tools/check_markdown_lint.py documents`.
- If links changed, also run `python3 scripts/tools/audit_and_fix_links.py documents`.

## Validation Commands

```bash
make ci-quick
make ci
bash scripts/run_comprehensive_review.sh
```

## Environment Notes

- If you touch Python dependencies, update `docker/Dockerfile` and `docker/requirements.txt` together.
- Prefer repository docs and checked-in scripts over agent-specific guesses.
- Keep runtime entrypoint files thin; update the canonical docs in `agents/` first.
