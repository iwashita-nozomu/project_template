# Goal
<!--
@dependency-start
responsibility Defines this repository's local goal loop contract.
upstream design README.md repository entrypoint
upstream implementation tools/agent_tools/goal_loop.py consumes this contract
@dependency-end
-->

## Loop Contract

- goal_status: achieved
- run_safety_cap: 0
- current_iteration: 0
- active_run_id:
- stop_reason: no active repo-local goal

## Objective

No active repo-local goal is set.

## Exit Criteria

- [x] G0: No active repo-local goal is pending.

## Backlog

## Loop Log

- initialized repo-local placeholder goal.
