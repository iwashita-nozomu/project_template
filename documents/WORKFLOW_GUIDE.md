# ユーザー向けワークフローガイド

この文書は、この template を使う人の入口です。
shared workflow canon の正本は `vendor/agent-canon/` にありますが、日常作業ではまず root 側のこの文書から入ります。

## 最初に見るもの

- `README.md`
- `QUICK_START.md`
- `documents/README.md`
- `agents/README.md`
- `docker/README.md`

## 作業の型

- 実装変更:
  - `documents/implementation-waterfall-workflow.md`
- tuning / 実験つき改善:
  - `documents/adaptive-improvement-workflow.md`
  - `documents/research-workflow.md`
  - `documents/experiment-workflow.md`
- 長文 / 学術文書:
  - `documents/long-form-writing-workflow.md`
  - `documents/academic-writing-workflow.md`
  - `documents/paper-writing-workflow.md`
- `main` 統合:
  - `documents/main-integration-workflow.md`
- worktree 運用:
  - `documents/worktree-lifecycle.md`
  - `documents/notes-lifecycle.md`
- shared canon 変更:
  - `documents/agent-canon-pr-workflow.md`
  - `documents/agent-canon-subtree-migration.md`

## 日常の進め方

1. task の型を決める
1. 必要な workflow 文書を読む
1. baseline を確認する
1. 実装、文書、テストを同じ pass でそろえる
1. closeout 前に validation を通す

## よく使う確認

```bash
make ci-quick
make ci
make docs-check
make agent-checks
make docker-build-check
```

## shared canon を触るとき

- shared canon の正本は `vendor/agent-canon/` です。
- root の runtime view を直接編集しません。
- 変更後は次を使います。

```bash
bash tools/sync_agent_canon.sh link-root
bash tools/sync_agent_canon.sh check
make agent-canon-pr-check
```

## 補足

- workflow の role routing と subagent policy は `agents/` 側を正本にします。
- root 側の文書は template 利用者向けの案内を優先します。
- `vendor/agent-canon/` 側の文書は agent-canon 自体の保守説明を優先します。
