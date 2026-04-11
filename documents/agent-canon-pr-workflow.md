# agent-canon PR ワークフロー

この文書は template repo 側から shared canon を直すときの手順です。
template の branch、PR、merge、upstream `agent-canon` sync を 1 本で扱います。

## 使う場面

- `vendor/agent-canon/` 配下を編集した
- shared runtime surface を増減した
- `tools/sync_agent_canon.sh` の link / copy spec を変えた
- shared workflow、skill、subagent、agent helper を直した

## 基本ルール

- shared canon の正本は `vendor/agent-canon/` です。
- shared canon 変更は dedicated branch / dedicated PR に分けます。
- root 側の symlink view や synced copy を直接編集しません。

## 標準手順

1. `vendor/agent-canon/` 側を編集する
1. 派生 repo 由来の shared canon 差分なら proposal branch へ push して出所を分ける
1. root surface を再同期する
1. shared canon 用 check を流す
1. template 側 PR を作る
1. `main` merge 後に upstream `agent-canon` へ push する

```bash
bash tools/update_agent_canon.sh proposal-branch
bash tools/update_agent_canon.sh push-proposal
bash tools/sync_agent_canon.sh link-root
bash tools/sync_agent_canon.sh check
make agent-canon-pr-check
```

merge 後:

```bash
git checkout main
git pull --ff-only origin main
bash tools/sync_agent_canon.sh push
```

## PR 本文

- changed surfaces
- validation
- file 構成変更の有無
- upstream sync plan

`.github/PULL_REQUEST_TEMPLATE/agent_canon.md` を使います。

## 参照先

- `vendor/agent-canon/documents/agent-canon-pr-workflow.md`
- `documents/main-integration-workflow.md`
- `documents/agent-canon-subtree-migration.md`
