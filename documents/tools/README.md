# ツール入口

このディレクトリは、repo で使う補助ツールの入口です。
詳細な台帳ではなく、いま残すべき実行導線だけを整理します。

## よく使うもの

- `scripts/ci/run_all_checks.sh`
  - 主要なチェックをまとめて実行します。
- `scripts/ci/run_docs_checks.sh`
  - repo-wide の Markdown 体裁とリンク監査をまとめて実行します。
- `scripts/ci/run_container_pack.py`
  - repo 定義の runtime pack を build / smoke します。
- `scripts/ci/run_in_repo_container.py`
  - repo workspace を mount した container command を実行します。
- `scripts/ci/run_codex_in_repo_container.py`
  - nested Codex を canonical container 内で起動します。
- `scripts/run_comprehensive_review.sh`
  - repo 全体の確認をまとめて実行します。
- `scripts/run_pytest_with_logs.sh`
  - Python テストをログ付きで実行します。
- `scripts/tools/check_markdown_lint.py`
  - Markdown の体裁確認です。
- `scripts/tools/audit_and_fix_links.py`
  - Markdown のリンク監査です。
- `scripts/agent_tools/bootstrap_agent_run.py`
  - agent 実行の入口です。
- `scripts/worktree_start.sh`
  - worktree kickoff の user-facing 入口です。
- `scripts/push_origin.sh`
  - commit 後の canonical push 入口です。

## 補足

- `setup_worktree.sh` などの branch/worktree 補助は例外運用用です。
- 既定運用は `main` であり、通常作業の入口にはしません。

## 参照先

- [scripts/README.md](/mnt/l/workspace/project_template/scripts/README.md)
- [TOOLS_DIRECTORY.md](/mnt/l/workspace/project_template/documents/tools/TOOLS_DIRECTORY.md)
