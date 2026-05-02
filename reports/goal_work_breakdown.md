# Goal Work Breakdown
<!--
@dependency-start
responsibility Records executable TODO units derived from goal.md.
upstream implementation ../vendor/agent-canon/tools/agent_tools/goal_loop.py generates this plan
@dependency-end
-->

## Summary

- goal_file: `/mnt/l/workspace/project_template/goal.md`
- goal_status_field: `achieved`
- goal_loop_status: `achieved`
- next_action: `close_goal_loop`
- open_exit_criteria: `0`
- open_backlog_items: `0`

## Work Units

| Unit ID | Source | Work To Do | Evidence To Produce | Status |
| ------- | ------ | ---------- | ------------------- | ------ |
| none | none | No unchecked goal items. | closeout evidence | complete |

## Schedule Transfer Rule

- Copy every open `GW*` row into the run bundle `schedule.md` before editing.
- Do not start implementation from a bare objective without this breakdown.
- If `NEXT_ACTION=run_next_iteration`, create the next iteration slice from the first open work unit.
