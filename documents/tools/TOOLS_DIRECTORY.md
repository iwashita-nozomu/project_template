# ツール目録

テンプレートとして残す主要ツールだけを列挙します。

## CI・検証

- `scripts/ci/run_all_checks.sh`
- `scripts/ci/run_docs_checks.sh`
- `scripts/run_comprehensive_review.sh`
- `scripts/run_pytest_with_logs.sh`

## 文書整備

- `scripts/tools/check_markdown_lint.py`
- `scripts/tools/audit_and_fix_links.py`
- `scripts/tools/fix_markdown_docs.py`
- `scripts/tools/find_similar_documents.py`

## agent 補助

- `scripts/agent_tools/bootstrap_agent_run.py`
- `scripts/agent_tools/validate_role_write_scope.py`

## 例外運用

- `scripts/setup_worktree.sh`
- `scripts/tools/create_worktree.sh`

これらは branch/worktree を使う特別な場合だけ使います。
