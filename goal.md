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

- goal_status: active
- run_safety_cap: 1
- current_iteration: 1
- active_run_id: 20260505-134238-execute-checklist-md-repository-audit
- stop_reason:

## Objective

Execute `checklist.md` as the current repository goal. Audit the current
`project_template` repository against every checklist section, classify the
pre-existing dirty file, fix any fix-now failures found during the audit, and
record objective-specific evidence in the run bundle.

## Exit Criteria

- [ ] G1: `checklist.md` is treated as the active repo goal and this file names the run bundle.
- [ ] G2: A prompt-to-artifact checklist maps every checklist section to concrete evidence.
- [ ] G3: Git, remote, AgentCanon latest, MCP, runtime surfaces, dependency graph, workflow, tooling, Docker/devcontainer, reuse/OOP, artifact, and derived-repo checks are executed or explicitly classified with evidence.
- [ ] G4: Pre-existing dirty files are classified and either preserved as user scope or intentionally committed with evidence.
- [ ] G5: Full-repo dependency review and static analysis pass after any fixes.
- [ ] G6: GitHub Actions workflows and PR checklists are reorganized for submodule-aware checkout, least-privilege CI, and explicit review evidence.
- [ ] G7: The run closes with no unchecked checklist item, validation failure, commit/push item, or AgentCanon sync item remaining in scope.

## Backlog

- [ ] B1: Freeze request clauses and schedule from `checklist.md`.
- [ ] B2: Run the checklist commands and collect evidence in the run bundle.
- [ ] B3: Reorganize `.github/workflows/` and PR checklist templates without duplicating canon responsibilities.
- [ ] B4: Fix any audit failure that is in scope for this repo and preserve unrelated user changes.
- [ ] B5: Re-run dependency review, agent checks, docs checks, and CI after fixes.
- [ ] B6: Update closeout artifacts, commit/push tracked changes, and mark the goal achieved only after the completion audit passes.

## Loop Log

- 2026-05-05 iteration 1 started: active thread goal is `checklist.md をゴールに設定して実行して`; run bundle `reports/agents/20260505-134238-execute-checklist-md-repository-audit/` created; initial MCP inventory pass; initial git status shows pre-existing `.devcontainer/devcontainer.json` dirty change.
- 2026-05-05 scope update: user added GitHub workflow reorganization and PR checklist review to the active goal.
