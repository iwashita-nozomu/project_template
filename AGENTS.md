# Agent Instructions

This repository keeps human-maintained agent canon under `agents/`.
Use this file as the runtime entrypoint for Codex and GitHub Copilot agents.

## Read First

- `README.md`
- `documents/README.md`
- `agents/README.md`
- `agents/canonical/README.md`

## Repo Defaults

- Human-facing primary language is Japanese.
- The repository default integration branch is `main`.
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

## Skills

- Canonical project skills for Codex/Copilot agent mode live in `.agents/skills/`.
- Claude-compatible mirrors live in `.claude/skills/`.
- Legacy GitHub-specific skill artifacts were moved to `agents/legacy/`.

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
