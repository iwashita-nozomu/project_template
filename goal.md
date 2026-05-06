# Goal
<!--
@dependency-start
responsibility Defines the repository-wide improvement backlog created from the 2026-05-06 file-by-file audit pass.
upstream design README.md repository entrypoint
upstream design AGENTS.md repository runtime policy and closeout contract
upstream design documents/SHARED_RUNTIME_SURFACES.md shared AgentCanon surface policy
upstream design documents/agent-canon-subtree-migration.md AgentCanon vendoring and migration policy
upstream implementation tools/agent_tools/goal_loop.py consumes this contract
downstream implementation tools/sync_agent_canon.sh applies AgentCanon submodule update routes
@dependency-end
-->

## Loop Contract

- goal_status: active
- run_safety_cap: 20
- current_iteration: 4
- active_run_id: 20260506-051028-full-repository-review-backlog-for-submo
- stop_reason:

## Objective

Turn the repository into a clean submodule-era template by resolving the file-by-file review findings recorded below. The backlog is intentionally broad: it treats `AGENTS.md`, shared runtime views, AgentCanon update flow, dependency manifests, GitHub workflows, Copilot/PR templates, evals, Docker/devcontainer, tooling, and stale subtree language as first-class improvement surfaces.

## Audit Scope

- Template tracked files scanned: 249.
- AgentCanon tracked files scanned: 513.
- Total tracked review surface: 762 files.
- Primary review commands used for intake:
- `python3 tools/agent_tools/check_mcp_inventory.py --require repo_mcp_server`
- `make agent-canon-ensure-latest`
- `git ls-files`
- `git -C vendor/agent-canon ls-files`
- `rg ... subtree|submodule|AgentCanon|AGENTS.md|Copilot|PULL_REQUEST_TEMPLATE`
- `bash tools/agent_tools/run_repo_dependency_review.sh --fail-missing`
- Intake note: an initial full dependency review emitted 28 potential missing-manifest classifications in root shared views / AgentCanon-linked surfaces, but the immediate rerun passed. This goal keeps dependency-tool hardening and regression coverage items so that YAML-frontmatter, H1-first Markdown, symlink, and submodule classifications do not flap.

## Iteration Log

- 2026-05-06 iteration 1: Updated `vendor/agent-canon/ROOT_AGENTS.md` through the root `AGENTS.md` shared view to define the submodule-first AgentCanon update flow, root shared-surface edit rules, closeout product/artifact gate split, independent diff-check exception model, eval artifact handling, workflow-monitor token requirements, and `goal_loop_status` completion gating. Added `review-submodule` / `align-main` tooling for AgentCanon submodule diff classification and safe main alignment. Added the static-analysis language-directory feedback to I171 without increasing the 200-item backlog size.
- 2026-05-06 iteration 2: Cleaned template product tree by removing tracked historical `reports/agents/...` run bundles and generated report Markdown files, expanded `.gitignore` so root `reports/*.md` stays generated state, and updated submodule-first README / AgentCanon migration / PR checklist evidence for I021-I040.
- 2026-05-06 iteration 3: Rewrote `vendor/README.md`, AgentCanon `AGENTS.md`, AgentCanon `README.md`, and `documents/SHARED_RUNTIME_SURFACES.md` to make submodule pin the normal path, isolate legacy subtree wording, list `.gitmodules` as template-local runtime contract, and document root synced-copy / GitHub symlink / standalone-only surfaces for I041-I060.
- 2026-05-06 iteration 4: Locked dependency-manifest top-of-file policy by documenting frontmatter / H1 allowance, full-repo strict review stability, and regression tests for SKILL.md frontmatter, Markdown H1, shell/TOML comments, symlink root views, and the I067-I080 agent runtime surfaces.

## Exit Criteria

- [ ] G1: Every item I001-I200 is resolved, explicitly deferred with owner/date, or split into a new tracked goal.
- [ ] G2: `AGENTS.md` and `vendor/agent-canon/ROOT_AGENTS.md` reflect the submodule-era workflow and no longer describe the normal path as subtree/snapshot.
- [ ] G3: AgentCanon update flow is documented and tooled around submodule pin update, upstream AgentCanon PR, root view sync, template pin commit, and derived-repo propagation.
- [ ] G4: Full repo dependency review passes: `bash tools/agent_tools/run_repo_dependency_review.sh --fail-missing`.
- [ ] G5: Shared surface drift check passes: `bash tools/sync_agent_canon.sh check`.
- [ ] G6: AgentCanon PR gate passes: `make agent-canon-pr-check`.
- [ ] G7: Template checks pass: `make agent-checks`, `make docs-check`, `make ci`, and Docker/Jupyter smoke when environment is available.
- [ ] G8: Independent review confirms no stale subtree-only guidance remains in user-facing README, AGENTS, workflow, PR template, or tool help surfaces.

## Backlog

- [x] I001: Add an `AGENTS.md` section named `AgentCanon Submodule Update Flow` that states the canonical order: update AgentCanon repo, push AgentCanon main or PR, update template submodule pin, run `link-root`, validate, then push template.
- [x] I002: Replace `vendor/agent-canon/ snapshot` wording in root `AGENTS.md` with `vendor/agent-canon submodule pin` wording where the normal path is submodule-based.
- [x] I003: Keep `legacy subtree` wording in `AGENTS.md` only in a compatibility paragraph that explicitly says it is not the default path.
- [x] I004: Add an `AGENTS.md` rule that missing shared-surface files must be checked in template root, `vendor/agent-canon`, standalone AgentCanon, `.gitmodules`, and `documents/SHARED_RUNTIME_SURFACES.md` before recreating files.
- [x] I005: Add an `AGENTS.md` rule that AgentCanon changes in a template PR must not be accepted unless the standalone AgentCanon PR/checklist path is considered first.
- [x] I006: Add an `AGENTS.md` rule that root shared-surface edits must be made in `vendor/agent-canon` unless the surface is intentionally template-local.
- [x] I007: Add an `AGENTS.md` rule that `goal.md` is always repo-local and must not be restored as a shared symlink.
- [x] I008: Add an `AGENTS.md` closeout gate requiring `git submodule status vendor/agent-canon` evidence.
- [x] I009: Add an `AGENTS.md` closeout gate requiring AgentCanon GitHub main SHA and template submodule pin SHA to be recorded when the task touches shared canon.
- [x] I010: Add an `AGENTS.md` closeout gate requiring local bare mirror status only when the task scope mentions `/mnt/git` or local mirror propagation.
- [x] I011: Split `AGENTS.md` closeout prohibitions into product gates and artifact gates so agents do not conflate product diff validation with run-bundle bookkeeping.
- [x] I012: Add an `AGENTS.md` exception model for independent diff-check when the runtime forbids spontaneous subagent spawn and the user has not requested multi-agent work.
- [x] I013: Add an `AGENTS.md` positive rule that if the user explicitly asks for multi-agent work, a read-only diff-check agent must be spawned before closeout.
- [x] I014: Add an `AGENTS.md` rule that `task_close.py` output is the mechanical closeout authority for run bundles.
- [x] I015: Add an `AGENTS.md` rule that eval feedback actions must be fixed in artifacts before final response, not merely acknowledged in chat.
- [x] I016: Add an `AGENTS.md` rule that `workflow_monitoring.md` must contain machine-readable tokens accepted by `evaluate_agent_run.py`.
- [x] I017: Add an `AGENTS.md` rule that `goal_loop_status` controls whether an active goal can be returned as complete.
- [x] I018: Add an `AGENTS.md` rule that `NEXT_ACTION=run_next_iteration` blocks completion for adaptive-improvement-loop work.
- [x] I019: Add an `AGENTS.md` rule that `NEXT_ACTION=close_goal_loop` allows final closeout only after validations and push evidence are present.
- [x] I020: Add an `AGENTS.md` rule that root `AGENTS.md` itself is always an allowed target during workflow-wide reviews.

- [x] I021: Keep `documents/agent-canon-subtree-migration.md` path for compatibility while giving the document a submodule-first title.
- [x] I022: Keep `documents/agent-canon-subtree-migration.md` only as a migration/legacy reference if a rename would break too many links.
- [x] I023: Rewrite the first half of `documents/agent-canon-subtree-migration.md` so submodule is the default model and subtree is legacy compatibility.
- [x] I024: Move historical `subtree add / pull / push` guidance into a clearly labeled legacy appendix.
- [x] I025: Replace `committed snapshot` language in README files with `submodule pin` language where clone behavior now depends on submodule checkout.
- [x] I026: Add a short `git clone --recurse-submodules` quickstart to root README.
- [x] I027: Add a `git submodule update --init --recursive` recovery command to root README.
- [x] I028: Add a derived-repo AgentCanon update sequence to root README using `make agent-canon-update-plan` and `make agent-canon-update`.
- [x] I029: Document when to run `git submodule sync vendor/agent-canon`.
- [x] I030: Document how to repair a detached or stale `vendor/agent-canon` worktree.
- [x] I031: Document the difference between AgentCanon GitHub `origin/main`, template `origin/main`, and local bare mirrors.
- [x] I032: Document that `.gitmodules` is part of the runtime contract and must be reviewed in AgentCanon update PRs.
- [x] I033: Add an explicit `submodule pin changed` section to the AgentCanon PR template.
- [x] I034: Add an explicit `submodule pin unchanged` justification field to the default PR template.
- [x] I035: Add a template PR checklist item requiring `actions/checkout` jobs that need canon to use `submodules: true`.
- [x] I036: Add a template PR checklist item requiring `persist-credentials: false` unless a workflow explicitly needs write credentials.
- [x] I037: Add a template PR checklist item requiring `permissions:` to be set at workflow or job level.
- [x] I038: Add a template PR checklist item requiring `concurrency:` review for long-running CI.
- [x] I039: Add a PR checklist field for `AgentCanon GitHub SHA`.
- [x] I040: Add a PR checklist field for `template submodule SHA`.

- [x] I041: Update `vendor/README.md` to stop calling `vendor/agent-canon` a subtree snapshot in the normal path.
- [x] I042: Update `vendor/README.md` commands so submodule plan, review, apply, proposal, status, and link-root are explained before legacy subtree commands.
- [x] I043: Update `vendor/README.md` to remove `pull` and `push` from the recommended derived-repo path unless they route through submodule semantics.
- [x] I044: Add a `Legacy subtree operations` warning block to `vendor/README.md`.
- [x] I045: Update `vendor/agent-canon/AGENTS.md` to say standalone AgentCanon repo is source, while template uses submodule pin, not subtree snapshot.
- [x] I046: Update `vendor/agent-canon/AGENTS.md` to replace `subtree 内の変更` with `AgentCanon tree changes`.
- [x] I047: Update `vendor/agent-canon/README.md` duplicate `.github/PULL_REQUEST_TEMPLATE/agent_canon.md` bullets.
- [x] I048: Update `vendor/agent-canon/README.md` to clarify which `.github` files are standalone-only, root-synced copies, and template-side symlink views.
- [x] I049: Update `documents/SHARED_RUNTIME_SURFACES.md` to separate submodule-default behavior from legacy subtree behavior.
- [x] I050: Update `documents/SHARED_RUNTIME_SURFACES.md` to list `.gitmodules` as a template-local surface with AgentCanon dependency.
- [x] I051: Update `documents/SHARED_RUNTIME_SURFACES.md` to list root `AGENTS.md` as a symlink target according to actual file mode.
- [x] I052: Add a generated shared-surface audit command to `documents/SHARED_RUNTIME_SURFACES.md`.
- [x] I053: Add a root-copy surface table for `.github/workflows/agent-coordination.yml`.
- [x] I054: Add a GitHub symlink surface table for `.github/copilot-instructions.md`.
- [x] I055: Add a GitHub symlink surface table for `.github/AGENTS.md`.
- [x] I056: Add a root-copy surface table for `.github/PULL_REQUEST_TEMPLATE/agent_canon.md`.
- [x] I057: Add a standalone-only surface table for `vendor/agent-canon/.github/PULL_REQUEST_TEMPLATE.md`.
- [x] I058: Add a rule that root copy surfaces must name their AgentCanon source in the file header.
- [x] I059: Add a rule that root copy surfaces must be compared against vendor source by `sync_agent_canon.sh check`.
- [x] I060: Add a rule that root copy surface changes require a source-side diff or a documented intentional override.

- [x] I061: Lock the full repo dependency review baseline so `run_repo_dependency_review.sh --fail-missing` remains stable across repeated runs.
- [x] I062: Decide whether dependency header tools should allow YAML frontmatter before the dependency manifest for `SKILL.md`.
- [x] I063: Decide whether dependency header tools should allow H1 title before the dependency manifest in Markdown docs.
- [x] I064: Add tests for dependency header detection with YAML frontmatter plus HTML comment blocks.
- [x] I065: Add tests for dependency header detection with TOML and shell comment syntax.
- [x] I066: Add tests for dependency header detection through symlink root views.
- [x] I067: Add regression coverage for `.agents/skills/codex-task-workflow/SKILL.md` dependency scan classification.
- [x] I068: Add regression coverage for `.claude/skills/adaptive-improvement-loop/SKILL.md` dependency scan classification.
- [x] I069: Add regression coverage for `.claude/skills/codex-task-workflow/SKILL.md` dependency scan classification.
- [x] I070: Add regression coverage for `.codex/README.md` dependency scan classification.
- [x] I071: Add regression coverage for `ROOT_AGENTS.md` missing/broken shared surface classification.
- [x] I072: Add regression coverage for `agents/TASK_WORKFLOWS.md` dependency scan classification.
- [x] I073: Add regression coverage for `agents/USER_GUIDE_JA.md` dependency scan classification.
- [x] I074: Add regression coverage for `agents/skills/catalog.yaml` dependency scan classification.
- [x] I075: Add regression coverage for `agents/skills/worktree-start.md` dependency scan classification.
- [x] I076: Add regression coverage for `agents/task_catalog.yaml` dependency scan classification.
- [x] I077: Add regression coverage for `agents/workflows/adaptive-improvement-workflow.md` dependency scan classification.
- [x] I078: Add regression coverage for `agents/workflows/agent-canon-pr-workflow.md` dependency scan classification.
- [x] I079: Add regression coverage for `agents/workflows/agent-learning-workflow.md` dependency scan classification.
- [x] I080: Add regression coverage for `agents/workflows/experiment-workflow.md` dependency scan classification.
- [ ] I081: Add regression coverage for `agents/workflows/implementation-waterfall-workflow.md` dependency scan classification.
- [ ] I082: Add regression coverage for `documents/BRANCH_SCOPE.md` dependency scan classification.
- [ ] I083: Add regression coverage for `documents/algorithm-implementation-boundary.md` dependency scan classification.
- [ ] I084: Add regression coverage for `documents/codex-configuration-reference.md` dependency scan classification.
- [ ] I085: Add regression coverage for `documents/coding-conventions-project.md` dependency scan classification.
- [ ] I086: Add regression coverage for `documents/coding-conventions-reviews.md` dependency scan classification.
- [ ] I087: Add regression coverage for `documents/conventions/python/20_benchmark_policy.md` dependency scan classification.
- [ ] I088: Add regression coverage for `documents/experiment-critical-review.md` dependency scan classification.
- [ ] I089: Add regression coverage for `documents/tools/README.md` dependency scan classification.
- [ ] I090: Add regression coverage for `documents/worktree-lifecycle.md` dependency scan classification.
- [ ] I091: Add regression coverage for `memory/AGENT_PHILOSOPHY.md` dependency scan classification.
- [ ] I092: Add regression coverage for `memory/USER_PREFERENCES.md` dependency scan classification.
- [ ] I093: Add regression coverage for `notes/README.md` dependency scan classification.
- [ ] I094: Add regression coverage for `notes/guardrails/engineering_avoidances.md` dependency scan classification.
- [ ] I095: Add dependency graph tests that distinguish root symlink path from vendor source path.
- [ ] I096: Add dependency graph output that groups missing headers by realpath owner.
- [ ] I097: Add dependency review output that says whether the failure is product file, root view, symlink, or submodule source.
- [ ] I098: Add a `--allow-frontmatter` flag only if the repo accepts that policy in docs.
- [ ] I099: Add a `--explain-missing` mode that prints first 20 lines and detected header reason.
- [ ] I100: Add a CI target that runs dependency review against both root view and `vendor/agent-canon` directly.

- [x] I101: Review `tools/sync_agent_canon.sh` route names and ensure submodule routes are presented before subtree routes.
- [ ] I102: Review `tools/sync_agent_canon.sh status` output for stale `subtree / snapshot` wording.
- [ ] I103: Review `tools/sync_agent_canon.sh snapshot` alias and decide whether to deprecate it in user-facing help.
- [ ] I104: Review `tools/sync_agent_canon.sh pull` semantics in submodule mode and decide whether it should refuse or redirect to `ensure-latest`.
- [ ] I105: Review `tools/sync_agent_canon.sh push` semantics in submodule mode and decide whether it should require a proposal branch.
- [ ] I106: Review `make agent-canon-update-plan` output for derived repos with stale submodule pins.
- [ ] I107: Review `make agent-canon-update` safety when the parent repo is dirty but the submodule is clean.
- [ ] I108: Review `make agent-canon-proposal-branch` behavior for submodule changes created in derived repos.
- [ ] I109: Review `make agent-canon-push-proposal` behavior for GitHub remote versus local bare mirror.
- [ ] I110: Review `make agent-canon-pr-check` so it validates `.gitmodules`, submodule URL, and submodule SHA evidence.
- [ ] I111: Add a smoke test for `make agent-canon-ensure-latest` when already current submodule.
- [ ] I112: Add a smoke test for `make agent-canon-ensure-latest` when submodule remote is ahead.
- [ ] I113: Add a smoke test for `make agent-canon-ensure-latest` when submodule has local commits.
- [ ] I114: Add a smoke test for `make agent-canon-ensure-latest` when `.gitmodules` URL differs from submodule origin URL.
- [ ] I115: Add a smoke test for `bash tools/sync_agent_canon.sh link-root` after submodule update.
- [ ] I116: Add a smoke test that `goal.md` remains repo-local after `link-root`.
- [ ] I117: Add a smoke test that root `.github/agent-coordination.yml` matches vendor source after `link-root`.
- [ ] I118: Add a smoke test that root `.github/copilot-instructions.md` matches vendor source after `link-root`.
- [ ] I119: Add a smoke test that root `.github/PULL_REQUEST_TEMPLATE/agent_canon.md` matches vendor source after `link-root`.
- [ ] I120: Add a smoke test that standalone AgentCanon `.github/PULL_REQUEST_TEMPLATE.md` is not copied to root default PR template by accident.

- [ ] I121: Review `.github/workflows/ci.yml` for submodule checkout in every job that uses AgentCanon-backed tools.
- [ ] I122: Review `.github/workflows/docker-build.yml` for submodule checkout before Docker build context validation.
- [ ] I123: Review `.github/workflows/agent-coordination.yml` for duplicated checkout blocks and consider YAML anchors or generated workflow composition.
- [ ] I124: Add a workflow lint that counts checkout steps without `submodules: true` when AgentCanon paths are referenced.
- [ ] I125: Add a workflow lint that rejects `persist-credentials: true` unless a job has documented write intent.
- [ ] I126: Add a workflow lint that rejects missing `permissions:` on workflows.
- [ ] I127: Add a workflow lint that warns on workflows missing `concurrency:` when jobs are long-running.
- [ ] I128: Add a workflow lint that checks root copy workflow header points to vendor source.
- [ ] I129: Add a workflow lint that checks AgentCanon workflow source header points to its PR workflow.
- [ ] I130: Add a workflow lint that checks PR template checklist contains validation evidence, dependency evidence, and submodule evidence.
- [ ] I131: Add a Copilot workflow acceptance test that `.github/copilot-instructions.md` links `agents/workflows/github-copilot-workflow.md`.
- [ ] I132: Add a Copilot workflow acceptance test that standalone AgentCanon PR template is discoverable from AgentCanon README.
- [ ] I133: Add a Copilot workflow acceptance test that template AgentCanon PR template is discoverable from root `.github/AGENTS.md`.
- [ ] I134: Add GitHub branch protection documentation for template main.
- [ ] I135: Add GitHub branch protection documentation for AgentCanon main.
- [ ] I136: Add `gh pr create` guidance for AgentCanon changes that start in a derived repo.
- [ ] I137: Add PR body examples for AgentCanon pin-only updates.
- [ ] I138: Add PR body examples for AgentCanon source changes plus template pin update.
- [ ] I139: Add PR body examples for root-only template workflow changes.
- [ ] I140: Add PR body examples for Copilot-only instructions changes.

- [ ] I141: Review `agents/workflows/github-copilot-workflow.md` for clear separation between Copilot limits and Codex closeout gates.
- [ ] I142: Review `agents/workflows/agent-canon-pr-workflow.md` for submodule-era sequencing.
- [ ] I143: Review `agents/workflows/derived-agent-canon-diff-workflow.md` for derived repo submodule changes.
- [ ] I144: Review `agents/workflows/main-integration-workflow.md` for submodule merge behavior.
- [ ] I145: Review `agents/workflows/token-efficient-codex-workflow.md` for subagent spawn restrictions and explicit user permission requirements.
- [ ] I146: Review `agents/workflows/adaptive-improvement-workflow.md` for `goal.loop_status` iteration enforcement.
- [ ] I147: Review `agents/workflows/implementation-waterfall-workflow.md` for current design/review stage count after workflow expansion.
- [ ] I148: Review `agents/workflows/hypothesis-validation-workflow.md` for code dependency versus header dependency separation.
- [ ] I149: Review `agents/workflows/workflow_monitoring.md` or equivalent docs for machine-readable eval tokens.
- [ ] I150: Review `agents/TASK_WORKFLOWS.md` for any stale family names or changed review stacks.
- [ ] I151: Review `agents/task_catalog.yaml` for tasks that should now select AgentCanon submodule workflow.
- [ ] I152: Review `agents/canonical/CODEX_WORKFLOW.md` for run bundle requirements that are too heavy for planning-only tasks.
- [ ] I153: Review `agents/canonical/CODEX_SUBAGENTS.md` for explicit-spawn runtime limitation wording.
- [ ] I154: Review `.codex/config.toml` max thread/runtime values against current subagent budget policy.
- [ ] I155: Review `.codex/hooks.json` and hook scripts for MCP preflight and goal loop injection.
- [ ] I156: Review `.codex/README.md` for stale setup instructions after submodule migration.
- [ ] I157: Review `mcp/repo_mcp_server.py` for goal loop status fields needed by active goal workflows.
- [ ] I158: Review `mcp/repo_mcp_server.sh` for cwd robustness in derived repos.
- [ ] I159: Review `tools/agent_tools/check_mcp_inventory.py` for clearer remediation output.
- [ ] I160: Review `tools/agent_tools/goal_loop.py` for 200-item backlog scaling and summary output.

- [ ] I161: Review `tools/agent_tools/evaluate_agent_run.py` so its required tokens are documented in workflow docs.
- [ ] I162: Review `tools/agent_tools/task_close.py` so independent diff-check requirements are feasible when subagent spawn is runtime-gated.
- [ ] I163: Review `tools/agent_tools/workflow_monitor.py` for easier one-command closeout token recording.
- [ ] I164: Review `tools/agent_tools/bootstrap_agent_run.py` for misleading `skipped_source_canon` output in template contexts.
- [ ] I165: Review `tools/agent_tools/agent_team.py` OOP readability findings and split large orchestration functions.
- [ ] I166: Review `tools/agent_tools/analyze_oop_readability.py` for its own high complexity findings.
- [ ] I167: Review `tools/agent_tools/vector_search.py` for index freshness and ignored path handling.
- [ ] I168: Review `tools/agent_tools/check_static_any.py` coverage for root and AgentCanon Python files.
- [ ] I169: Review `tools/agent_tools/check_hardcoded_numbers.py` thresholds and false positives in config-heavy files.
- [ ] I170: Review `tools/agent_tools/check_log_helper_names.py` for Python and shell helper naming coverage.
- [ ] I171: Organize static-analysis tools by language-specific directories such as `tools/static_analysis/python/`, `tools/static_analysis/cpp/`, and `tools/static_analysis/common/`, then expose an integrated `make review-backlog-scan` target that runs file inventory, stale wording search, dependency review, workflow lint, and OOP baseline.
- [ ] I172: Add a generated Markdown report for file-by-file review findings under ignored `reports/agents/<run-id>/`.
- [ ] I173: Add a machine-readable JSON report for file inventory and surface classification.
- [ ] I174: Add a `--submodule-aware` option to review tools where parent repo and submodule repo both need scanning.
- [ ] I175: Add a `--root-only` option to review tools where submodule internals must be excluded.
- [ ] I176: Add a `--agentcanon-only` option to review tools for standalone AgentCanon runs.
- [ ] I177: Add tests that root symlink surfaces do not create duplicate false positives in OOP/static scans.
- [ ] I178: Add tests that dependency scan can report root path and real source path together.
- [ ] I179: Add tests that vector search does not index `.git` or submodule object databases.
- [ ] I180: Add tests that `rg`-based sweep examples exclude `.git/**` by default.

- [ ] I181: Review `docker/README.md` for any wording that treats AgentCanon/template remote names as Docker image state.
- [ ] I182: Review `.devcontainer/devcontainer.json` for host SSH/Codex/GitHub auth mount clarity.
- [ ] I183: Review `.devcontainer/docker-compose.generated.yml` generation and whether the generated file should remain tracked.
- [ ] I184: Review `docker/packs/default.toml` for `jupyter` smoke command coverage.
- [ ] I185: Review `docker/register_safe_directories.sh` for submodule vendor path enumeration.
- [ ] I186: Review `documents/linux-wsl-host-requirements.md` for submodule checkout and host auth requirements.
- [ ] I187: Review `documents/template-github-remote.md` for template GitHub canonical remote policy.
- [ ] I188: Review `documents/agent-canon-github-remote.md` for submodule URL and local mirror guidance.
- [ ] I189: Review `documents/tools/README.md` for `sync_agent_canon.sh` user-facing route descriptions.
- [ ] I190: Review `documents/repo-local-tool-imports.md` for moving derived repo tools into AgentCanon under submodule workflow.
- [ ] I191: Review `documents/result-log-retention-and-visualization.md` for run bundle and ignored artifact policy.
- [ ] I192: Review `documents/object-oriented-design.md` for how OOP readability findings become improvement backlog items.
- [ ] I193: Review `documents/algorithm-implementation-boundary.md` for math/implementation boundary checks in large refactors.
- [ ] I194: Review `documents/coding-conventions-project.md` for submodule-era AgentCanon update conventions.
- [ ] I195: Review `documents/coding-conventions-reviews.md` for full-repo review expectations and diff-check independence.
- [ ] I196: Review `documents/codex-configuration-reference.md` for current Codex settings, goals, hooks, and subagents.
- [ ] I197: Review `documents/project-template-overview-slides.md` so it says submodule pin, not committed snapshot, where appropriate.
- [ ] I198: Review `documents/README.md` index for stale, renamed, or legacy AgentCanon vendoring docs.
- [ ] I199: Review `QUICK_START.md` for submodule checkout and `make agent-canon-ensure-latest` ordering.
- [ ] I200: After completing the backlog, run an independent file-by-file review pass again and replace this goal with a smaller residual backlog.

## Loop Log

- 2026-05-06 iteration 0 created: MCP inventory passed; repo was clean; `make agent-canon-ensure-latest` reported `already_current_submodule`; file inventory found 249 template tracked files and 513 AgentCanon tracked files; stale subtree/snapshot wording remains in user-facing docs and tools; an initial dependency review reported 28 potential classifications but immediate rerun passed, so regression coverage is retained in the backlog.
