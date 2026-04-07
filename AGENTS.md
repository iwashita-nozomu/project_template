# Agent Instructions

This repository keeps the shared agent canon in `vendor/agent-canon/`.
Root `agents/`, `.agents/`, `.claude/`, `.codex/agents`, `.codex/README.md`, selected `documents/`, and selected `scripts/` are runtime views into that snapshot.

Use this file as the runtime entrypoint for Codex and GitHub Copilot agents.

## Read First

- `README.md`
- `documents/WORKFLOW_GUIDE.md`
- `agents/README.md`
- `agents/canonical/README.md`
- `agents/canonical/CODEX_WORKFLOW.md`
- `documents/AGENTS_COORDINATION.md`
- `docker/README.md`

## Product Defaults

- Human-facing primary language is Japanese.
- The default integration branch is `main`.
- Product-scoped Codex runtime settings live in `.codex/config.toml`.
- Product rules stay in `documents/`, implementation in `python/`, environment guidance in `docker/`.

## Shared Canon

- Shared workflow, role, skill, and review policy live under `agents/`.
- Shared coordination and review docs live in `documents/AGENTS_COORDINATION.md`, `documents/REVIEW_PROCESS.md`, `documents/implementation-waterfall-workflow.md`, and `documents/workflow-references.md`.
- Shared agent support scripts live in `scripts/agent_tools/` and `scripts/tools/mirror_skill_shims.py`.
- If a shared surface drifts, repair it with `bash scripts/sync_agent_canon.sh link-root`.
- Keep this file thin. If a rule is reusable across products, update the shared canon, not this wrapper.

## Validation

- `make agent-checks`
- `make ci-quick`
- `make docs-check`
