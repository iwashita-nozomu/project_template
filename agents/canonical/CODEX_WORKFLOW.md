# Codex Workflow

この文書は、Codex でこの repo を扱うときの標準フローです。
会話の過去文脈に依存せず、毎回同じ順序で進められるようにします。

## Start Here

1. `AGENTS.md` を読む
1. `agents/README.md` を読む
1. `agents/skills/README.md` を読む
1. `documents/coding-conventions-python.md` を読む
1. `agents/TASK_WORKFLOWS.md` で task family を決める
1. `agents/canonical/ARTIFACT_PLACEMENT.md` で文書の置き場を決める
1. specialist が必要なら `agents/canonical/CODEX_SUBAGENTS.md` を読む
1. 必要なら `.agents/skills/` から該当 skill を読む

## Task Classification

次の 4 つから 1 つ選びます。

- `Scoped Change`
- `Research-Driven Change`
- `Large Delivery`
- `Platform And Environment`

迷った場合:
- 外部調査や比較実験が必要なら `Research-Driven Change`
- Docker / CI / dependency を触るなら `Platform And Environment`
- 大きくなければまず `Scoped Change`

## Minimal Skill Set

Codex では、まず `agents/skills/README.md` から必要最小限の skill だけ選びます。

- repo 入口確認:
  - `repo-onboarding`
- workflow 選択:
  - `agent-orchestration`
- 文書置き場:
  - `artifact-placement`
- run bundle / specialist 起動:
  - `subagent-bootstrap`
- validation:
  - `static-validation`
- Python diff:
  - `python-review`
- Markdown diff:
  - `md-style-check`
- review:
  - `change-review`
- literature and prior art:
  - `literature-survey`
- research outer loop:
  - `research-workflow`
- experiment report:
  - `report-review`
- research-wide review pack:
  - `research-perspective-review`

## Execution Flow

### 1. Intake

- 変更対象と acceptance criteria を短く固定する
- 不明点が多い場合だけ追加探索する

### 2. Workflow Selection

- `agents/TASK_WORKFLOWS.md` から family を 1 つ選ぶ
- family をまたぐ場合も、主 family を 1 つ決める

### 3. Placement

- run 固有のメモは `reports/agents/<run-id>/`
- repo-wide の恒久文書は `agents/` か `documents/`
- 知見の蓄積は `notes/`

### 4. Optional Run Bootstrap

次の場合だけ bundle を作ります。

- specialist handoff を明示したい
- review artifact を残したい
- 長めの task で run 単位の記録が必要
- subagent と parent の責務を分けたい

コマンド:

    python3 scripts/agent_tools/bootstrap_agent_run.py \
      --task "short task summary" \
      --owner "codex"

### 5. Implementation

- 正本は `agents/` と `documents/` から先に直す
- runtime entrypoint は薄く保つ
- skill は repo 正本を置き換えず、導線だけを担う

### 6. Validation

- agent runtime / skill 変更では `make agent-checks`
- まず `make ci-quick`
- 必要に応じて `make ci`
- Python 変更では `pyright`、`pytest python/tests/`、`ruff check python/ --select D,E,F,I,UP` を確認する
- 文書変更では markdown / link check を使う
- report を閉じる前には `documents/experiment-report-style.md` を確認する
- 研究系 task では `critical-review` と `report-review` の decision state を確認し、必要なら `research-perspective-review` を追加する

### 7. Closeout

- 何を変えたか
- 何を確認したか
- 何を確認していないか

この 3 点を短く残して完了する

## Codex-Specific Rules

- `AGENTS.md` は Codex の最初の入口として保つ
- `.agents/skills/` を正規 skill path とする
- Codex 専用事情でも、再利用可能なルールは `agents/` に昇格する
- 会話文脈にだけ依存する運用は repo 正本にしない
