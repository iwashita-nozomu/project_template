# ワークフロー目録

この文書は、テンプレートに残す自動化入口と、人手判断が必要な運用を整理します。

## 自動化済みの入口

- `scripts/ci/run_all_checks.sh`
  - 主要な静的チェックとテストをまとめて実行します。
- `scripts/ci/run_docs_checks.sh`
  - repo-wide の Markdown 体裁とリンク監査をまとめて実行します。
- `scripts/ci/check_docker_build.sh`
  - Dockerfile の build 可否と最小限の runtime smoke check を確認します。
- `scripts/ci/run_container_pack.py`
  - repo 定義の runtime pack を build / smoke します。
- `scripts/ci/run_in_repo_container.py`
  - repo workspace を mount した container command を実行します。
- `scripts/ci/run_python_in_dockerfile.py`
  - Python file を rule ベースで container 実行します。
- `scripts/ci/run_codex_in_repo_container.py`
  - nested Codex を canonical container 内で起動します。
- `scripts/run_pytest_with_logs.sh`
  - Python テストのログ付き実行入口です。Python を使う場合だけ使います。
- `scripts/run_comprehensive_review.sh`
  - repo 全体の確認をまとめて実行します。
- `scripts/tools/check_markdown_lint.py`
  - Markdown 体裁を確認します。
- `scripts/tools/check_markdown_math.py`
  - Markdown 数式記法を確認します。
- `scripts/tools/audit_and_fix_links.py`
  - Markdown 内リンクを確認します。
- `scripts/tools/fix_markdown_docs.py`
  - Markdown の機械的な整形を補助します。
- `scripts/tools/find_similar_documents.py`
  - 類似文書の検出を補助します。
- `scripts/worktree_start.sh`
  - worktree kickoff の user-facing 入口です。
- `scripts/push_origin.sh`
  - commit 後の canonical push 入口です。

## 人手判断が必要な作業

- 実験結果の採否判断
- 規約変更の正本反映
- どの知見を `notes/` に残すかの取捨選択
- 不要 branch や古い補助文書の削除判断
- 環境依存ツールを repo 正本へ採用するかの判断

## 不足している自動化

- README 群の stale 記述を継続検出する checker
- `notes/` の古い参照や絶対パスを監査する checker
- 実験 report の最小必須項目を確認する lint
- local GitHub Actions replay を repo 汎用に扱う runner

## 使い分け

- 日常の確認は `make ci-quick`
- 仕上げ前の確認は `make ci`
- 文書確認は `make docs-check`
- Docker 変更の確認は `make docker-build-check`
- host Docker socket 依存の確認は `make docker-build-check-host-docker`
- repo 全体の点検は `bash scripts/run_comprehensive_review.sh`
- 実験運用は `documents/experiment-workflow.md`
- 実験つきの改造 loop は `agents/skills/experiment-change-loop.md`
- 環境依存ツール導入案は `agents/skills/environment-maintenance.md` と `agents/templates/environment_change_proposal.md`
