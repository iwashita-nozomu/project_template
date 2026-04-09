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
bash tools/sync_agent_canon.sh status
bash tools/sync_agent_canon.sh pull
bash tools/sync_agent_canon.sh push
```

## 使い分け

- template 利用者:
  - root 文書と root entrypoint から読む
- shared canon 保守者:
  - `vendor/agent-canon/` 側を source of truth として編集する

## 参照先

- `documents/agent-canon-pr-workflow.md`
- `vendor/agent-canon/documents/agent-canon-subtree-migration.md`
- `vendor/agent-canon/documents/SHARED_RUNTIME_SURFACES.md`
