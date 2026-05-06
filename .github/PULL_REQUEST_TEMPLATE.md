# Pull Request Checklist
<!--
@dependency-start
responsibility Documents the default pull request checklist for template repository changes.
upstream design ../AGENTS.md defines repository closeout requirements
upstream design ../documents/repository-audit-checklist.md defines repository audit checklist
upstream design ../documents/REVIEW_PROCESS.md defines review evidence requirements
upstream design ../documents/template-github-remote.md defines template GitHub remote policy
@dependency-end
-->

## Summary

- What changed:
- Why this change is needed:
- User/request clause or issue:

## Scope Classification

- [ ] Template-local change only
- [ ] AgentCanon submodule pin update only
- [ ] Shared AgentCanon source change under `vendor/agent-canon/`
- [ ] Docker/devcontainer/runtime change
- [ ] GitHub Actions or PR checklist change
- [ ] Documentation-only change

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
- [ ] Private AgentCanon submodule access is covered by repository secret `AGENT_CANON_REPO_TOKEN`, or the PR explains why the workflow does not need it.
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
