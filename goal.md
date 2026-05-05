# Goal
<!--
@dependency-start
responsibility Defines the top-level goal loop contract for this repository.
upstream design README.md repository entrypoint
upstream design checklist.md repository audit checklist objective
downstream implementation tools/agent_tools/goal_loop.py consumes this contract
@dependency-end
-->

## Loop Contract

- goal_status: achieved
- run_safety_cap: 1
- current_iteration: 1
- active_run_id: 20260505-134238-execute-checklist-md-repository-audit
- stop_reason: checklist audit completed, validation passed, AgentCanon synced, and final push prepared

## Objective

Execute `checklist.md` as the current repository goal. Audit the current
`project_template` repository against every checklist section, classify the
pre-existing dirty file, fix any fix-now failures found during the audit, and
record objective-specific evidence in the run bundle.

## Exit Criteria

- [x] G1: `checklist.md` is treated as the active repo goal and this file names the run bundle.
- [x] G2: A prompt-to-artifact checklist maps every checklist section to concrete evidence.
- [x] G3: Git, remote, AgentCanon latest, MCP, runtime surfaces, dependency graph, workflow, tooling, Docker/devcontainer, reuse/OOP, artifact, and derived-repo checks are executed or explicitly classified with evidence.
- [x] G4: Pre-existing dirty files are classified and either preserved as user scope or intentionally committed with evidence.
- [x] G5: Full-repo dependency review and static analysis pass after any fixes.
- [x] G6: GitHub Actions workflows and PR checklists are reorganized for submodule-aware checkout, least-privilege CI, and explicit review evidence.
- [x] G7: The run closes with no unchecked checklist item, validation failure, commit/push item, or AgentCanon sync item remaining in scope.

## Backlog

- [x] B1: Freeze request clauses and schedule from `checklist.md`.
- [x] B2: Run the checklist commands and collect evidence in the run bundle.
- [x] B3: Reorganize `.github/workflows/` and PR checklist templates without duplicating canon responsibilities.
- [x] B4: Fix any audit failure that is in scope for this repo and preserve unrelated user changes.
- [x] B5: Re-run dependency review, agent checks, docs checks, and CI after fixes.
- [x] B6: Update closeout artifacts, commit/push tracked changes, and mark the goal achieved only after the completion audit passes.

## Loop Log

- 2026-05-05 iteration 1 started: active thread goal is `checklist.md をゴールに設定して実行して`; run bundle `reports/agents/20260505-134238-execute-checklist-md-repository-audit/` created; initial MCP inventory pass; initial git status shows pre-existing `.devcontainer/devcontainer.json` dirty change.
- 2026-05-05 scope update: user added GitHub workflow reorganization and PR checklist review to the active goal.
- 2026-05-05 iteration 1 completed: AgentCanon commits `89a881b`, `b93143f`, and `908cb19` were pushed; template submodule pin synced; GitHub Actions, PR templates, Copilot workflow, Docker Jupyter smoke, dependency review, docs check, CI, and Docker build check all passed. Final template push is the closeout action after this achieved goal commit.
