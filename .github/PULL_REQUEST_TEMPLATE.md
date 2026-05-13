# Pull Request Checklist
<!--
@dependency-start
responsibility Documents the default pull request checklist for template repository changes.
upstream design ../AGENTS.md defines repository closeout requirements
upstream design ../documents/repository-audit-checklist.md defines repository audit checklist
upstream design ../documents/REVIEW_PROCESS.md defines review evidence requirements
upstream design ../documents/template-github-remote.md defines template GitHub remote policy
upstream design ../documents/github-copilot-configuration.md defines Copilot configuration and PR-template routing
upstream design ../vendor/agent-canon/issues/README.md defines AgentCanon durable operational issue storage
@dependency-end
-->

## Summary

- What changed:
- Why this change is needed:
- User/request clause or issue:
- Template / derived project PR context:

## Scope Classification

- [ ] Template-local change only
- [ ] AgentCanon submodule pin update only
- [ ] Shared AgentCanon source change under `vendor/agent-canon/`
- [ ] Docker/devcontainer/runtime change
- [ ] GitHub Actions or PR checklist change
- [ ] Documentation-only change

## Repository Separation

- [ ] This is a Template / derived project PR, not a standalone AgentCanon repository PR.
- [ ] Standalone AgentCanon source changes, if needed, were opened or merged in the AgentCanon repository first.
- [ ] Changes under `vendor/agent-canon/` also use `.github/PULL_REQUEST_TEMPLATE/agent_canon.md` evidence.
- [ ] The standalone AgentCanon `.github/PULL_REQUEST_TEMPLATE.md` was not copied into the template root.

## Plan Mode Evidence

- [ ] Plan mode was used before non-trivial template, Copilot, GitHub Actions, PR-template, AgentCanon sync, or shared runtime-surface changes.
- [ ] Written plan is included in the PR body, issue, run bundle, or linked comment when the runtime did not expose an explicit Plan mode.
- [ ] Trivial-change exception is explained below when Plan mode was not used.

Plan / exception:

## PR Mutation Authority

- [ ] This PR only required inspection, branch push, PR creation, title/body update, evidence comments, draft-state preservation, or conversion to draft.
- [ ] Merge / close / ready-for-review / reviewer request / review dismissal / auto-merge / branch deletion was explicitly authorized by the user for this task, or was not performed.
- [ ] If merge, close, or ready-for-review is still required, the blocker and required human/maintainer action are recorded below instead of being guessed from `gh` availability.
- [ ] If `pr_mutation_authority: github_copilot_merge_when_green` is used, the PR has Copilot-visible evidence and local Codex did not perform the merge.

Authority / blocker notes:

## Copilot / Automation Output

- goal `pr_mutation_authority`:
- `COPILOT_PR_AUTHORITY=`:
- `COPILOT_PR_DECISION=`:
- `COPILOT_PR_CHECKS=`:
- `COPILOT_VISIBLE_EVIDENCE=`:
- `COPILOT_BLOCKER=`:
- `gh pr checks` summary:

## Operational Findings / Issues

- [ ] If this template / derived PR exposed an AgentCanon workflow, tool, memory, eval, or closeout defect, `vendor/agent-canon/issues/README.md` was reviewed.
- [ ] Existing durable AgentCanon findings were searched in `vendor/agent-canon/issues/open/`, `vendor/agent-canon/memory/`, `vendor/agent-canon/notes/failures/`, relevant workflow docs, and prior run-bundle evidence when available.
- [ ] New AgentCanon operational findings were written to `vendor/agent-canon/issues/open/AC-YYYYMMDD-<slug>.md`, `vendor/agent-canon/memory/`, or `vendor/agent-canon/notes/failures/` before closeout, or no new durable finding is required.
- [ ] Raw `rg` hits, if used to choose the fix surface, were expanded with `run_repo_dependency_review.sh --search-hits-file` and dependency-expanded edit scope is cited below.

Issue / edit-scope evidence:

## Copilot Configuration Impact

- [ ] `documents/github-copilot-configuration.md` was reviewed.
- [ ] `.github/copilot-instructions.md` changed / reviewed / not affected.
- [ ] `.github/instructions/*.instructions.md` changed / reviewed / not affected.
- [ ] `.github/agents/*.md` changed / reviewed / not affected.
- [ ] GitHub Copilot MCP, `copilot-setup-steps.yml`, or Copilot environment settings changed / reviewed / not affected.
- [ ] PR template routing still separates Template / derived project PRs, AgentCanon pin PRs, and standalone AgentCanon repository PRs.

Impact notes:

## Reuse And Drift

- [ ] Existing tools, docs, workflows, and fixtures were checked before adding new surfaces.
- [ ] Root shared surfaces were not edited directly when the source of truth is `vendor/agent-canon/`.
- [ ] `bash tools/sync_agent_canon.sh check` passes or drift is explained below.
- [ ] Pre-existing dirty files are classified and not silently reverted.

## Validation Evidence

- [ ] `bash tools/agent_tools/run_repo_dependency_review.sh --fail-missing`
- [ ] `make agent-checks`
- [ ] `make docs-check`
- [ ] `make ci`
- [ ] GitHub workflow / PR template changes: `python3 tools/ci/check_github_workflows.py`
- [ ] Docker/devcontainer changes: `bash tools/docker_dependency_validator.sh`
- [ ] GitHub workflow changes: every `actions/checkout` job uses `submodules: false`, then runs `bash .github/scripts/checkout_agent_canon_submodule.sh` when AgentCanon is needed.
- [ ] Private AgentCanon submodule access is covered by repository secret `AGENT_CANON_REPO_TOKEN`, `AGENT_CANON_REPO_SSH_KEY` from a read-only deploy key, or the PR explains why the workflow does not need it.
- [ ] GitHub workflow changes: `persist-credentials: false` is set unless the job has documented write intent.
- [ ] GitHub workflow changes: `permissions:` is set at workflow or job level.
- [ ] GitHub workflow changes: `concurrency:` is present or explicitly not needed.

Validation output:

```text
paste the key pass lines here
```

## AgentCanon Evidence

- [ ] `vendor/agent-canon` pin matches AgentCanon GitHub `main`, or the intentional delta is explained.
- [ ] `vendor/agent-canon` pin is unchanged and the reason is documented below.
- [ ] `.gitmodules` was reviewed when AgentCanon URL, branch, or checkout behavior is in scope.
- [ ] GitHub Actions private submodule checkout behavior was reviewed when CI, Docker, Copilot, or PR automation is in scope.
- [ ] AgentCanon changes were committed and pushed to `iwashita-nozomu/agent-canon`.
- [ ] Template submodule pin was committed after AgentCanon push.
- [ ] Memory changes were persisted with `python3 tools/agent_tools/persist_agent_memory.py --commit --push`.

- AgentCanon GitHub SHA:
- template submodule SHA:
- submodule pin unchanged justification:

## Review Focus

- correctness risk:
- stale documentation risk:
- workflow / CI risk:
- follow-up explicitly not included:
