# @dependency-start
# contract reference
# responsibility Upstream sync note:.
# upstream design ../../agents/workflows/agent-canon-pr-workflow.md agent-canon PR workflow
# upstream design ../../vendor/agent-canon/issues/README.md durable operational issue storage
# upstream implementation ../../tools/agent-canon/ci/check_github_workflows.py validates PR checklist and workflow conventions
# downstream implementation ../../tools/agent-canon/agent_tools/issue_sync.py validates local/GitHub issue sync state
# upstream design ../../vendor/agent-canon/templates/documents/README.md canonical template owner and projection boundary
# upstream design ../../vendor/agent-canon/documents/operations/issue-label-taxonomy.md issue/eval routing taxonomy
# upstream design ../AGENTS.md GitHub subtree instructions
# dependency-end

## PR Essence

- Problem / user request:
- Design intent:
- Canonical owner:
- Replaceable responsibility unit:
- Behavior or contract delta:

## Scope and Identity

- Changed surface: `.github/...` only
- Canonical route: `workflow=<family>`, `skills=$agent-orchestration`, `review=<value>`
- Mutation authority: `PARENT_DIRECT_WRITE_EXCEPTION` (if any) / delegated handoff route
- Identity: `local_head=<SHA>` `target_head=<SHA>`

## Changed-Surface Validation

- [ ] `git diff --name-only` shows only `.github` paths (excluding README or generated artifacts)
- [ ] `python3 tools/agent-canon/ci/check_github_workflows.py` passed
- [ ] `python3 tools/agent-canon/ci/check.py --schema` for each touched workflow
- [ ] Manual YAML parse for each changed `.yml`:
  - `ci.yml`
  - `docker-build.yml`
  - `agent-coordination.yml`
  - `agent-improvement-guide.yml`
- [ ] `git diff --check` clean (no whitespace errors)
- [ ] Any workflow surface evidence in changed files is consistent with runtime owner comments

## Alternatives / Independent Review

Only add an alternative table when an actual behavior choice or failure-mode risk remains unresolved:

| option | mechanism | risk | decision |
| --- | --- | --- | --- |
| keep existing path | existing | existing baseline preserved | selected |
| simplify to one canonical route | this PR | reduced template/config surface | selected |

## Operational Notes

- This PR intentionally omits universal issue-memory-failure mirror sweep and standalone Copilot review workflow requirements for this .github-only surface pass.
- Priority is correct route/identity visibility plus touched-surface validation.
- `agent-improvement-guide` is manual/explicit only for this PR path.

## Outcome

- validation command:
- what it proves:
- unresolved risk / follow-up:
