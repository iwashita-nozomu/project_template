# ワークフロー目録

この文書は、テンプレートに残す自動化入口と、人手判断が必要な運用を整理します。

## 自動化済みの入口

- `scripts/ci/run_all_checks.sh`
  - 主要な静的チェックとテストをまとめて実行します。
- `scripts/run_pytest_with_logs.sh`
  - Python テストのログ付き実行入口です。Python を使う場合だけ使います。
- `scripts/run_comprehensive_review.sh`
  - repo 全体の確認をまとめて実行します。
- `scripts/tools/check_markdown_lint.py`
  - Markdown 体裁を確認します。
- `scripts/tools/audit_and_fix_links.py`
  - Markdown 内リンクを確認します。
- `scripts/tools/fix_markdown_docs.py`
  - Markdown の機械的な整形を補助します。
- `scripts/tools/find_similar_documents.py`
  - 類似文書の検出を補助します。

## 人手判断が必要な作業

- 実験結果の採否判断
- 規約変更の正本反映
- どの知見を `notes/` に残すかの取捨選択
- 不要 branch や古い補助文書の削除判断

## 不足している自動化

- README 群の stale 記述を継続検出する checker
- `notes/` の古い参照や絶対パスを監査する checker
- 実験 report の最小必須項目を確認する lint

## 使い分け

- 日常の確認は `make ci-quick`
- 仕上げ前の確認は `make ci`
- repo 全体の点検は `bash scripts/run_comprehensive_review.sh`
- 実験運用は `documents/experiment-workflow.md`
