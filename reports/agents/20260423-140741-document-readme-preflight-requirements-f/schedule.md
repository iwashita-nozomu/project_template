# Schedule

- Run ID: 20260423-140741-document-readme-preflight-requirements-f
- Task: document README preflight requirements for subagent and skill startup
- Owner: codex

## Stage Plan

| Stage | Owner Agent | Review Agent | Inputs | Exit Criteria | Status |
| ----- | ----------- | ------------ | ------ | ------------- | ------ |
| context-and-scope | parent codex | parent document-flow mindset | user request, README head, preference notes | top-of-file wording and scope are fixed | complete |
| implementation | parent codex | parent change-review mindset | README head block style, resolved clauses | README head contains the new warning with both subagent and skill startup requirements | complete |
| validation-and-closeout | parent codex | parent final-review mindset | README diff, docs checks, run bundle | docs validation passes, artifacts are populated, commit/push complete | complete |

## Clause Coverage

| Clause ID | Covered By Stage | Review Gate | Status |
| --------- | ---------------- | ----------- | ------ |
| R-C1 | context-and-scope, implementation, validation-and-closeout | README-head wording review | complete |
| R-C2 | context-and-scope, implementation, validation-and-closeout | README-head wording review | complete |
| R-N1 | implementation, validation-and-closeout | top-of-file placement review | complete |
| R-E1 | implementation, validation-and-closeout | README diff review | complete |
| R-E2 | validation-and-closeout | docs-check evidence | complete |

## Planned Work Units

<!-- This table is the canonical task TODO surface. Keep concrete work units and statuses here until closeout. -->

| Unit ID | Clause IDs | Owner | Completion Evidence | Next Gate | Status |
| ------- | ---------- | ----- | ------------------- | --------- | ------ |
| W1 | R-C1,R-C2 | codex | resolved clause mapping and README-head wording decision | implementation | complete |
| W2 | R-C1,R-C2,R-N1,R-E1 | codex | patched `README.md` | validation | complete |
| W3 | R-E2 | codex | passing docs validation plus commit/push evidence | closeout | complete |

## Task Completion Boundary

- No user-facing completion before the README head carries the new rule, docs validation passes, and the task artifacts and commit/push evidence are recorded.

## Explicit Subagents

- none; this is a single-file repo-local doc edit with one write scope, so parent direct handling is sufficient

## Reuse And Continuity Constraints

- preserve the existing README top note style using `> [!IMPORTANT]`
- keep the wording direct and operational, matching the repo's existing runtime instructions

## Risks

- the new warning must stay short enough for the README head but still cover both subagents and skills
- kickoff was initially blocked from automatic ensure-latest because the worktree carried a pre-existing shared-memory diff
