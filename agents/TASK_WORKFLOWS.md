# Agent Task Workflows

この文書は、repo で使う workflow family の正本です。
task を細かく増やしすぎず、少数の family に寄せて運用します。

## Workflow Families

### 1. Scoped Change

対象:
- 局所バグ修正
- 小規模な docs/test 同期
- CI failure の切り分け

標準フロー:
1. `manager`
1. `manager_reviewer`
1. `designer`
1. `design_reviewer`
1. `implementer`
1. `change_reviewer`
1. `final_reviewer`
1. `verifier`

### 2. Research-Driven Change

対象:
- 外部調査を伴う実装
- benchmark や比較実験を根拠にした改善

追加ロール:
- `researcher`
- `research_reviewer`
- `experimenter`
- `experiment_reviewer`

特徴:
- research と experiment を evidence として回す
- overclaim review を明示的に挟む

### 3. Large Delivery

対象:
- 新機能追加
- 大規模 refactor
- 複数 chunk に分ける delivery

追加ロール:
- `scheduler`
- `schedule_reviewer`

特徴:
- milestone と chunk 境界を先に固定する
- 逐次 review と最終 review を分ける

### 4. Platform And Environment

対象:
- Docker
- CI
- automation
- dependency / runtime upgrade

追加ロール:
- `infra_steward`
- `infra_reviewer`
- 必要に応じて `researcher`, `scheduler`, `experimenter`

特徴:
- rollout と rollback を先に考える
- repo ルール、環境、automation を同時に更新する

## 選び方

1. task が局所修正なら `Scoped Change`
1. 外部調査や比較実験が必要なら `Research-Driven Change`
1. chunk 設計が必要なら `Large Delivery`
1. 環境や automation を触るなら `Platform And Environment`

## 関連

- `agents/task_catalog.yaml`
- `agents/COMMUNICATION_PROTOCOL.md`
- `agents/canonical/ARTIFACT_PLACEMENT.md`
- `agents/canonical/CLI_ENTRYPOINTS.md`
- `documents/experiment-workflow.md`
- `documents/research-workflow.md`
