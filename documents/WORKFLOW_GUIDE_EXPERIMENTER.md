# 実験者向けワークフローガイド

この文書は、実験コード、比較実験、report、知見の carry-over を扱う利用者向けの入口です。
repo 全体の見取り図は `documents/WORKFLOW_GUIDE.md` を見てください。

## 最初に決めること

1. 問い
1. 比較対象
1. 成否判断
1. report の置き場

研究寄りの改善では、`documents/research-workflow.md` を outer loop、`documents/experiment-workflow.md` を run ごとの実務手順として使います。

## 主に触る場所

- 実験コード:
  - `experiments/<topic>/`
- report:
  - `experiments/report/`
- cross-run の知見:
  - `notes/experiments/`
  - `notes/themes/`
- 実験の正本手順:
  - `documents/experiment-workflow.md`
- research loop:
  - `documents/research-workflow.md`

## 標準フロー

1. 問い、仮説、比較条件を固定する
1. 実験 README に手順と出力先を書く
1. fresh run を実行する
1. result と report を同じ run 名でそろえる
1. 必要なら批判的 review を挟んで再実行する
1. cross-run の知見だけを `notes/` に残す

## 守ること

- partial run を正式結果として扱わない
- 結果だけを口頭運用にしない
- report と result path を対応づける
- 複数 run をまたぐ知見は `notes/` に切り出す

## よく使う確認

```bash
make ci-quick
python3 scripts/tools/check_markdown_lint.py --check experiments/report/<run_name>.md
python3 scripts/tools/audit_and_fix_links.py --check experiments
```

## review を伴うとき

research-driven な改善では、次を意識します。

- 比較条件が揃っているか
- overclaim していないか
- report が rerun / rewrite / extra validation を必要としていないか

詳細は次です。

- `documents/experiment-critical-review.md`
- `documents/experiment-report-style.md`
- `documents/research-workflow.md`
- `agents/skills/experiment-change-loop.md`

## close 条件

- fresh run の結果が保存されている
- report が更新されている
- 実験固有の知見と repo-wide ルールを混ぜていない
- 必要な review loop を閉じている
- commit と push が完了している
