# vendor

`vendor/` は、外部で管理される shared asset を、この repo に snapshot として取り込む場所です。

この template では、shared agent canon の取り込み先を次に固定します。

- `vendor/agent-canon/`

原則:
- product runtime の正面入口は root `AGENTS.md` と root `.codex/` に残します
- `vendor/agent-canon/` は shared canon の subtree snapshot として扱います
- shared canon の同期は [scripts/sync_agent_canon.sh](/mnt/l/workspace/project_template/scripts/sync_agent_canon.sh) から行います
- template repo には committed snapshot を残すので、`git clone <template>` 直後でも shared canon を参照できます
- root の `AGENTS.md`, `agents/`, `.agents/`, `.claude/`, `CLAUDE.md`, `.github/AGENTS.md`, `.github/copilot-instructions.md`, `.codex/config.toml`, `.codex/agents`, `.codex/README.md`, `documents/agent-canon-subtree-migration.md`, `documents/BRANCH_SCOPE.md`, `documents/AGENTS_COORDINATION.md`, `documents/REVIEW_PROCESS.md`, `documents/SKILL_IMPLEMENTATION_GUIDE.md`, `documents/WORKTREE_SCOPE_TEMPLATE.md`, `documents/implementation-waterfall-workflow.md`, `documents/workflow-references.md`, `documents/worktree-lifecycle.md`, `notes/themes/from_another_agent.md`, `notes/worktrees/README.md`, `notes/worktrees/WORKTREE_LOG_TEMPLATE.md`, `python/tests/agent_tools/__init__.py`, `python/tests/agent_tools/test_smoke_test_research_perspective_pack.py`, `python/tests/tools/test_mirror_skill_shims.py`, `scripts/agent_tools/`, `scripts/setup_worktree.sh`, `scripts/sync_agent_canon.sh`, `scripts/worktree_start.sh`, `scripts/tools/check_worktree_scopes.sh`, `scripts/tools/create_worktree.sh`, `scripts/tools/mirror_skill_shims.py` は、この snapshot を指す symlink view にします
- `documents/SHARED_RUNTIME_SURFACES.md` は shared runtime surface の ownership をまとめる正本です
- `.github/workflows/agent-coordination.yml` は、この snapshot を正本とする root 同期コピーにします

よく使うコマンド:

```bash
bash scripts/sync_agent_canon.sh link-root
bash scripts/sync_agent_canon.sh check
bash scripts/sync_agent_canon.sh snapshot
bash scripts/sync_agent_canon.sh add git@github.com:<org>/agent-canon.git
bash scripts/sync_agent_canon.sh pull
bash scripts/sync_agent_canon.sh push
bash scripts/sync_agent_canon.sh status
```

注意:
- `vendor/agent-canon/AGENTS.md` は、必要なら canon 開発 subtree 用 override としてだけ置きます
- product 全体の runtime discovery は root entrypoint に寄せます
- `check` は shared surface の drift を fail-fast で検出します
- `link-root` は shared surface の symlink と同期コピーを vendor 正本へ戻します。対象に未 commit の変更がある場合は、先に commit / stash するか、意図的な再同期だけ `AGENT_CANON_FORCE_RELINK=1` を使います
