# Project Template

実装、実験、文書、エージェント運用を 1 つの repo で扱うためのテンプレートです。
特定言語の専用テンプレートではありません。`python/` は任意の実装スロットの 1 つであり、必要に応じて `src/`、`include/`、`lib/`、`experiments/` を使い分けます。

この README は人間向けの入口です。エージェント向けの入口は `agents/README.md` です。

## このテンプレートに残すもの

- `documents/`
  - 規約、設計、開発環境、実験手法の正本です。
- `notes/`
  - 実験や調査をまたいで残したい知見、補助メモ、テーマ整理を置きます。
- `agents/`
  - エージェントチーム定義、運用ルール、workflow の正本です。
- `scripts/`
  - チェック、整形、補助運用の入口です。
- `docker/`
  - 共通開発環境の定義です。
- `experiments/`
  - 実験コード、run ごとの生成物、report を置く場所です。使わないプロジェクトでは空でも構いません。
- `python/`, `src/`, `include/`, `lib/`
  - 言語や実装形態に応じて使う実装スロットです。全部を埋める必要はありません。

## 基本方針

- 既定の統合先は `main` です。恒常的な複数 branch 運用はしません。
- 短期 branch は必要なときだけ切り、整理が済んだら `main` に戻します。
- `documents/` には正本だけを置きます。履歴説明や日付付きの途中報告は置きません。
- 実装変更では、必要なテストと文書更新を同じ変更でそろえます。
- 実験は 1 回の run を fresh 実行として扱い、途中停止 run を正式結果として継ぎ足しません。
- 言語固有の規約は補足として置きますが、repo 全体の入口は言語非限定で保ちます。

## まず読むもの

- `QUICK_START.md`
- `documents/README.md`
- `documents/conventions/README.md`
- 開発環境を触る場合は `docker/`
- 実験を行う場合は `documents/experiment-workflow.md`
- エージェントを使う場合は `agents/README.md`

## 日常の進め方

1. 何を変えるかを決めます。実装だけか、実験まで含むか、環境や文書更新が必要かを最初に切ります。
2. 変更前に `make ci-quick` を流して、壊れている前提を持ち込まないようにします。
3. 実装、実験コード、文書、必要なら `docker/` を更新します。
4. 仕上げに `make ci` か必要な個別チェックを流します。
5. 長期に残す判断や実験知見は `notes/` に移し、正本ルールは `documents/` に反映します。

## 実験を含むプロジェクトでの使い方

新規実験は次のような配置を基準にします。

```text
experiments/
├── report/
│   └── <run_name>.md
└── <topic>/
    ├── README.md
    ├── cases.*
    ├── experiment.*
    └── result/
        └── <run_name>/
```

- 1 回の run の report は `experiments/report/<run_name>.md`
- run ごとの生成物は `experiments/<topic>/result/<run_name>/`
- 複数 run をまたぐ知見は `notes/experiments/` または `notes/themes/`

実験方法論そのものは `documents/experiment-workflow.md` と `documents/research-workflow.md` を正本にします。

## よく使うコマンド

```bash
make ci-quick
make ci
make tools-help
```

## 詳細入口

- 規約と運用: `documents/README.md`
- 補助メモ: `notes/README.md`
- エージェント運用: `agents/README.md`
- スクリプト一覧: `scripts/README.md`
