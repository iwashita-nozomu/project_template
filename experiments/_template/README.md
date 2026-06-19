# Experiment Topic Template
<!--
@dependency-start
contract template
responsibility Documents Experiment Topic Template for this repository.
upstream design ../README.md experiments hub guidance
downstream implementation cases.py case scaffold
downstream implementation run.py run scaffold
@dependency-end
-->

このディレクトリは、新しい experiment topic を始めるための最小雛形です。
server 上でそのまま回せるように、`cases.py`、`run.py`、`config.yaml`、`notebooks/`、`result/` の入口をそろえています。

## Question

<!-- この topic が何を確かめる実験なのかを書く -->

## Comparison Target

<!-- main、baseline、reference method などを書く -->

## Visualization Notebook

可視化は `notebooks/` 配下の Jupyter notebook に置きます。Notebook は
`result/<run_name>/summary.json`、`cases.jsonl`、必要な `logs/` artifact を読み、
figure / table を作る入口です。formal run の起動や設定正本にはしません。

## Logs

各 run は `result/<run_name>/logs/` を持ちます。top-level の `run.log` は
managed runner の互換ログとして残し、追加 stdout / stderr、tool log、diagnostic
log は `logs/` 配下へ置きます。

## Standard Commands

smoke:

```bash
python3 tools/experiments/run_managed_experiment.py \
  --topic <topic> \
  --use-registered-command smoke
```

formal run:

```bash
python3 tools/experiments/run_managed_experiment.py \
  --topic <topic> \
  --use-registered-command formal
```

## Expected Outputs

- `result/<run_name>/run_manifest.json`
- `result/<run_name>/config.json`
- `result/<run_name>/eval_manifest.json`
- `result/<run_name>/run.log`
- `result/<run_name>/logs/`
- `result/<run_name>/summary.json`
- `result/<run_name>/cases.jsonl`
- `notebooks/<run_name>.ipynb` またはこの topic で固定した可視化 notebook
- `experiments/report/<run_name>.md`

## Notes

- `cases.py` は case 列の定義に集中させます。
- `run.py` は CLI、orchestration、summary 出力に集中させます。
- `experiments/registry.toml` に topic entry を追加し、`smoke_inner_command` と `formal_inner_command` を正本にします。
- registered command には `{config_path}` を含め、実験 script は `--config <path>` から JSON object を読みます。
- 追加で自動収集したい eval artifact がある場合は、`experiments/registry.toml` の `required_eval_artifacts` / `optional_eval_artifacts` に pattern を書きます。top-level managed file (`run_manifest.json`、`eval_manifest.json`、`run.log`) は pattern に入れてはいけません。
- formal run では `run_name` と protocol を固定した fresh 実行にします。
