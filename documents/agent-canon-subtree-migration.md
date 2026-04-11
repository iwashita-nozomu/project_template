# agent-canon subtree 構成

この文書は template 側から見た `agent-canon` subtree 構成の要約です。
詳細な inventory や maintainer 向け説明は `vendor/agent-canon/documents/agent-canon-subtree-migration.md` を見ます。

## 構成

- upstream repo:
  - `agent-canon`
- template 側の取り込み先:
  - `vendor/agent-canon/`
- root 側の runtime surface:
  - symlink view または synced copy

## 意味

- `git clone <template>` 直後でも shared canon を参照できます。
- worktree を切ると、その時点の `vendor/agent-canon/` snapshot が見えます。
- upstream `agent-canon` の最新が自動で入るわけではありません。

## 同期コマンド

```bash
bash tools/update_agent_canon.sh plan
bash tools/update_agent_canon.sh apply
bash tools/update_agent_canon.sh proposal-branch
bash tools/update_agent_canon.sh push-proposal
bash tools/sync_agent_canon.sh status
bash tools/sync_agent_canon.sh ensure-latest
bash tools/sync_agent_canon.sh pull
bash tools/sync_agent_canon.sh push
```

派生 repo で `agent-canon` だけ更新するときの既定入口は `update_agent_canon.sh` です。
`plan` は subtree 登録済みなら `subtree_pull`、metadata が無い clone なら snapshot import 系 route を出します。
project-local bare repo を後から登録するときは `bash tools/update_agent_canon.sh register-local-bare --bare-repo /mnt/git/<project>-agent-canon.git` を使います。
shared canon の差分を戻すときは `bash tools/update_agent_canon.sh push-proposal` を使い、repo ごとの proposal branch へ積みます。`bash tools/sync_agent_canon.sh push` は maintainer が整理後に upstream `agent-canon` の `main` を更新するときに使います。

task 開始時は `ensure-latest` を使います。
clean worktree なら upstream `agent-canon` の最新を必要時だけ取り込み、dirty worktree で stale が見つかれば停止します。
`agent-canon` remote が未設定で `/mnt/git/agent-canon.git` が存在する場合は、自動でその remote を追加します。
fresh clone で subtree metadata が無い場合でも、local snapshot が upstream の祖先である fast-forward 更新なら snapshot import に切り替えて取り込みます。
local と upstream が diverge している場合は上書きせず停止します。

## 使い分け

- template 利用者:
  - root 文書と root entrypoint から読む
- shared canon 保守者:
  - `vendor/agent-canon/` 側を source of truth として編集する

## 参照先

- `documents/agent-canon-pr-workflow.md`
- `vendor/agent-canon/documents/agent-canon-subtree-migration.md`
- `vendor/agent-canon/documents/SHARED_RUNTIME_SURFACES.md`
