# Experiment Notes

このディレクトリには、個別実験や比較検証の要約を置きます。
1 回の run に対応する一次 report は `experiments/report/` 側に置き、ここでは複数 run をまたぐ整理や判断を残します。

## 参照先

- `documents/experiment-workflow.md`
- `documents/research-workflow.md`
- `documents/experiment-critical-review.md`
- `documents/experiment-report-style.md`

## 推奨構成

- `Abstract`
- `Question and Context`
- `Protocol`
- `Results`
- `Discussion`
- `Limitations`
- `Critical Review`
- `Conclusion`

テンプレートは `REPORT_TEMPLATE.md` を使えます。

## 最低限残すもの

- 問い
- 比較対象
- run 名
- 主要 metric
- source artifact へのリンク
- 結果の要約
- 解釈と限界
- 次の action

## ルール

- partial run を正式結果として扱いません。
- raw ログや巨大生成物はここへ複製しません。
- 実験メモは topic 単位で分けます。
