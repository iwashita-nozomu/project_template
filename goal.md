# Goal
<!--
@dependency-start
responsibility Defines the top-level goal loop contract for this repository.
upstream design README.md repository entrypoint
downstream implementation tools/agent_tools/goal_loop.py consumes this contract
@dependency-end
-->

## Loop Contract

- goal_status: achieved
- run_safety_cap: 3
- current_iteration: 0
- active_run_id:
- stop_reason:

## Objective

Organize documentation and the AgentCanon update path, remove redundant files, and eliminate convention violations.

## Exit Criteria

- [x] G1: Repository dependency review passes with `bash tools/agent_tools/run_repo_dependency_review.sh --fail-missing`.
- [x] G2: Code dependency extraction is reviewed with `bash tools/agent_tools/scan_code_dependencies.sh` for the affected surface.
- [x] G3: OOP/readability analysis is run with `python3 tools/agent_tools/analyze_oop_readability.py` and findings are fixed or documented.
- [x] G4: Repo-wide static analysis or CI passes with `make ci`, or the documented fallback `python3 -m pyright` plus `python3 -m ruff check python tests --select D,E,F,I,UP`.
- [x] G5: Objective-specific completion evidence is recorded.

## Backlog

- [x] B1: Build the prompt-to-artifact checklist that maps objective clauses to files, commands, gates, and completion evidence.
- [x] B2: Survey existing docs, tools, tests, and reusable surfaces before adding or deleting anything; list reuse, consolidation, and deletion candidates.
- [x] B3: Execute one cohesive implementation slice that advances the selected related surfaces together instead of stopping after one micro-fix.
- [x] B4: Run dependency review, code dependency scan, OOP/readability, and task-relevant prompt/doc/convention checks; fix any failure in the same iteration.
- [x] B5: Refresh the goal work breakdown, close completed backlog items with evidence, and continue immediately if NEXT_ACTION still reports run_next_iteration.

## Loop Log

- iteration evidence: expanded AgentCanon goal loop default backlog in commit `50a27a8`; consolidated AgentCanon update docs and removed obsolete tool index in commit `a1ae42d`.
- validation evidence: `run_repo_dependency_review.sh --fail-missing` pass; `scan_code_dependencies.sh` pass; OOP/readability pass with score 74 and zero warn/error density; `make agent-checks`, `make docs-check`, and `make ci` pass.
- closeout evidence: `reports/agents/20260502-093419-organize-agentcanon-update-documentation/` records clause mapping, schedule GW1-GW10 complete, workflow monitoring, evaluation `140/140`, and no remaining follow-up.
