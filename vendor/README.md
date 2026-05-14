# vendor
<!--
@dependency-start
responsibility Documents vendor for this repository.
upstream design ../documents/agent-canon-subtree-migration.md shared canon submodule update and legacy migration contract
downstream design agent-canon/README.md vendored shared canon overview
@dependency-end
-->

`vendor/` は、外部で管理される shared asset を、この repo から pinned dependency として参照する場所です。

この template では、shared agent canon の取り込み先を次に固定します。

- `vendor/agent-canon/`

原則:
- product runtime の正面入口は root `AGENTS.md` と root `.codex/` に残します
- `vendor/agent-canon/` は shared canon の Git submodule pin として扱います
- shared canon の通常更新は [tools/update_agent_canon.sh](/mnt/l/workspace/project_template/tools/update_agent_canon.sh) から行います
- root の `AGENTS.md`, `agents/`, `.agents/`, `.claude/`, `CLAUDE.md`, `.github/AGENTS.md`, `.github/copilot-instructions.md`, `.codex/config.toml`, `.codex/agents`, `.codex/README.md`, `mcp/`, `documents/agent-canon-subtree-migration.md`, `documents/BRANCH_SCOPE.md`, `documents/AGENTS_COORDINATION.md`, `documents/REVIEW_PROCESS.md`, `documents/SHARED_RUNTIME_SURFACES.md`, `documents/SKILL_IMPLEMENTATION_GUIDE.md`, `documents/WORKFLOW_GUIDE.md`, `documents/WORKTREE_SCOPE_TEMPLATE.md`, `documents/experiment-workflow.md`, `documents/implementation-waterfall-workflow.md`, `documents/research-workflow.md`, `documents/workflow-references.md`, `documents/worktree-lifecycle.md`, `notes/themes/from_another_agent.md`, `notes/worktrees/README.md`, `notes/worktrees/WORKTREE_LOG_TEMPLATE.md`, `tests/agent_tools/__init__.py`, `tests/agent_tools/test_smoke_test_research_perspective_pack.py`, `tests/tools/test_mirror_skill_shims.py`, `tools/agent_tools/`, `tools/setup_worktree.sh`, `tools/sync_agent_canon.sh`, `tools/worktree_start.sh`, `tools/docs/check_worktree_scopes.sh`, `tools/docs/create_worktree.sh`, `tools/docs/mirror_skill_shims.py` は、この submodule pin を指す symlink view にします
- `documents/SHARED_RUNTIME_SURFACES.md` は shared runtime surface の ownership をまとめる正本です
- `.github/workflows/agent-coordination.yml` と `.github/PULL_REQUEST_TEMPLATE/agent_canon.md` は、この submodule pin を正本とする root 同期コピーにします

よく使うコマンド:

```bash
bash tools/update_agent_canon.sh plan
bash tools/update_agent_canon.sh apply
bash tools/update_agent_canon.sh merge-main-into-current
bash tools/sync_agent_canon.sh status
bash tools/sync_agent_canon.sh link-root
bash tools/sync_agent_canon.sh check
```

Legacy subtree operations:
- `bash tools/sync_agent_canon.sh pull` と `bash tools/sync_agent_canon.sh push` は subtree-era compatibility または maintainer 低レベル操作です
- submodule 化済み repo の通常更新では `update_agent_canon.sh plan -> apply` を使います
- submodule 内の local commit は `merge-main-into-current` で GitHub `main` を取り込み、通常の AgentCanon GitHub branch / PR に回します

注意:
- `vendor/agent-canon/AGENTS.md` は、standalone AgentCanon repo 用 entrypoint として扱います
- product 全体の runtime discovery は root entrypoint に寄せます
- `check` は shared surface の drift を fail-fast で検出します
- `link-root` は shared surface の symlink と同期コピーを vendor 正本へ戻します。対象に未 commit の変更がある場合は、先に commit / stash するか、意図的な再同期だけ `AGENT_CANON_FORCE_RELINK=1` を使います
