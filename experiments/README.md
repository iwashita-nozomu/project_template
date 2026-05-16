# Experiments Hub
<!--
@dependency-start
responsibility Documents Experiments Hub for this repository.
upstream design ../vendor/agent-canon/documents/experiment-registry.md experiment registry contract
downstream environment registry.toml template-local registry
@dependency-end
-->

<!--
@dependency-start
responsibility Documents repository-local experiment topic and report layout.
upstream design ../vendor/agent-canon/documents/experiment-registry.md defines managed experiment registry policy.
upstream implementation registry.toml defines active experiment topics.
downstream implementation _template provides the topic scaffold.
downstream implementation report stores per-run experiment reports.
@dependency-end
-->

`experiments/` は、server 上で回す実験コード、run ごとの生成物、1 run ごとの report をまとめる場所です。
この template では、topic ごとの実験コードと run artifact を同じ tree に寄せます。
shared canon では、このうち topic 共通の scaffold と report 導線だけを保持し、派生 repo ごとの `registry.toml` と `experiments/<topic>/` は root 側の正本に残します。

## 標準構成

```text
experiments/
├── registry.toml
├── report/
│   ├── README.md
│   └── <run_name>.md
└── <topic>/
    ├── README.md
    ├── cases.py
    ├── experimentcode.py
    └── result/
        └── <run_name>/
```

## まず使うもの

- `_template/`
  - 新しい topic を始めるときの最小雛形です。
- `registry.toml`
  - topic、entrypoint、formal run command、active branch の集中管理ファイルです。
- `report/README.md`
  - run report の置き方です。
- `tools/experiments/create_experiment_topic.py`
  - `_template/` から新しい topic を作り、registry entry も追加します。
- `tools/experiments/sync_experiment_registry_context.py`
  - current branch / worktree / scope file を registry に同期します。
- `tools/experiments/run_managed_experiment.py`
  - `run_manifest.json` と `run.log` を残しながら実験を実行する入口です。

## server 実行の既定

- fresh run は 1 つの `run_name` と 1 つの `result/<run_name>/` に閉じます。
- server 上の formal run は、できるだけ `run_managed_experiment.py` 経由で実行します。
- formal run でどの code を実行するかは `registry.toml` の `formal_inner_command` を正本にします。
- 主要生成物は次を基準にします。
  - `result/<run_name>/run_manifest.json`
  - `result/<run_name>/config.json`
  - `result/<run_name>/eval_manifest.json`
  - `result/<run_name>/run.log`
  - `result/<run_name>/summary.json`
  - `result/<run_name>/cases.jsonl`
- 1 回の run report は `experiments/report/<run_name>.md` に置きます。

## topic の作り始め

```bash
python3 tools/experiments/create_experiment_topic.py <topic>
```

コピーしたら、少なくとも次をその topic に合わせて書き換えます。

- `README.md`
- `cases.py`
- `experimentcode.py`
- `registry.toml` の topic entry
- 標準コマンド
- `Question:`
- `Comparison Target:`

## 実行例

```bash
python3 tools/experiments/run_managed_experiment.py \
  --topic _template \
  --use-registered-command smoke
```

この wrapper は、`registry.toml` の topic entry を見て command 実行前に result dir、`config.json`、report stub を初期化し、終了後に manifest を更新し、`summary.json` / `cases.jsonl` / `config.json` と registry で指定した追加 eval artifact を `eval_manifest.json` に収集します。top-level の `run_manifest.json`、`eval_manifest.json`、`run.log` は reserved managed file として eval collection の対象外です。

## Registry Check

```bash
python3 tools/ci/check_experiment_registry.py
make experiment-check
```

## Context Sync

branch / worktree を使う場合は、scope 更新後に次で registry metadata を合わせます。

```bash
python3 tools/experiments/sync_experiment_registry_context.py \
  --topic <topic> \
  --branch work/<topic>-YYYYMMDD \
  --workspace-root .worktrees/<branch-name>
```
