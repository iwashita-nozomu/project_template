# User Request Contract

- Run ID: 20260423-140741-document-readme-preflight-requirements-f
- Task: document README preflight requirements for subagent and skill startup
- Owner: codex
- Created At (UTC): 2026-04-23T14:07:41Z

## Gate Status

- all_clauses_resolved: yes
- forbidden_drift_detected: no
- deferred_clause_ids:
- unresolved_clause_ids:

## Requirements Resolution Sweep

- Searched `README.md`, `AGENTS.md`, `vendor/agent-canon/memory/USER_PREFERENCES.md`, `documents/SHARED_RUNTIME_SURFACES.md`, and the current README-top note style.
- Resolved from accumulated context:
  - the request is repo-local documentation, not a shared-canon workflow rewrite
  - the repo already has an `IMPORTANT` block at the README head for MCP startup, so the new rule should appear alongside it
  - the worktree was dirty at kickoff because of a pre-existing shared-memory preference note; that carryover was committed separately before closing this README task

## Resolved From Accumulated Context

| Clause ID | Resolved From | Evidence Path | Resolution | Remaining Risk |
| --------- | ------------- | ------------- | ---------- | -------------- |
| R-C1 | repo_or_code_precedent | `README.md` | add the new guidance as another top-of-file `IMPORTANT` notice rather than burying it lower in the document | none |
| R-C2 | durable_user_preference | `vendor/agent-canon/memory/USER_PREFERENCES.md` | interpret the request as requiring explicit, mechanical startup of both subagents and skills, with no silent fallback to parent-only handling | wording is concise, not a full workflow spec |

## Must-Do Clauses

| Clause ID | Source Bucket | User Wording Or Evidence | Operational Interpretation | Owner Stage | Evidence Path | Status |
| --------- | ------------- | ------------------------- | -------------------------- | ----------- | ------------- | ------ |
| R-C1 | current_request | `さぶエージェントの起動が甘いです．READMEの先頭に` | add a top-of-README warning that subagent startup must not be weak or assumed; required subagents must be explicitly and mechanically started | implementation | `README.md` | resolved |
| R-C2 | current_request | `それから，スキルも機械的に起動するように` | expand the same README-head warning so required skills are also started explicitly and mechanically, rather than implied or silently skipped | implementation | `README.md` | resolved |

## Must-Not-Do Clauses

| Clause ID | Source Bucket | Forbidden Drift | Why It Is Forbidden | Guard Stage | Evidence Path | Status |
| --------- | ------------- | --------------- | ------------------- | ----------- | ------------- | ------ |
| R-N1 | durable_user_preference | leave the new rule implicit, soft, or buried below the README entrypoint | the user explicitly asked for README-head visibility and repeatedly rejects weak startup behavior | implementation, review | `README.md` | resolved_clean |

## Completion Evidence Clauses

| Clause ID | Source Bucket | Required Evidence | Where It Must Appear | Owner Stage | Status |
| --------- | ------------- | ----------------- | -------------------- | ----------- | ------ |
| R-E1 | current_request | README head contains an explicit warning covering both subagents and skills | `README.md` | implementation, review | resolved |
| R-E2 | repo_or_code_precedent | docs validation passes after the README edit | `verification.txt` | validation | resolved |

## Source Bucket Rules

- Allowed buckets: `current_request`, `durable_user_preference`, `repo_or_code_precedent`, `domain_or_external_constraint`, `unknown_or_open_question`.
- Durable user preferences do not become task requirements unless the current request or repo evidence supports the conversion.
- Unknowns stay unresolved, deferred, or escalated; they are not converted into silent assumptions.
- Active must-do, must-not-do, and completion-evidence clauses must not use `unknown_or_open_question`; unresolved items must move to Deferred Or Rejected Clauses after the resolution sweep.
- Do not stop at the first ambiguity if accumulated notes, repo docs, local code, tests, or prior logs can resolve it without changing user intent.

## Deferred Or Rejected Clauses

| Clause ID | Reason | Escalation Or Follow-Up Path | Status |
| --------- | ------ | ---------------------------- | ------ |
| U-C1 | kickoff worktree was dirty because of a pre-existing shared-memory preference note | resolved by committing and pushing the carryover shared-memory change separately before closing this README task | resolved |

## Update Rule

- Every planning, design, implementation, and review artifact must cite the clause IDs it covers.
- If active work does not map to at least one must-do clause, stop and escalate instead of continuing.
- Closeout stays locked until every must-do and completion-evidence clause is resolved and every must-not-do clause remains clean.
