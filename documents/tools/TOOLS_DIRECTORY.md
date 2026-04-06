# ツール目録

テンプレートとして残す主要ツールだけを列挙します。

## CI・検証

- `scripts/ci/run_all_checks.sh`
- `scripts/ci/run_docs_checks.sh`
- `scripts/ci/run_container_pack.py`
- `scripts/ci/run_in_repo_container.py`
- `scripts/ci/run_python_in_dockerfile.py`
- `scripts/ci/run_codex_in_repo_container.py`
- `scripts/run_comprehensive_review.sh`
- `scripts/run_pytest_with_logs.sh`

## 文書整備

- `scripts/tools/check_markdown_lint.py`
- `scripts/tools/check_markdown_math.py`
- `scripts/tools/audit_and_fix_links.py`
- `scripts/tools/fix_markdown_docs.py`
- `scripts/tools/find_similar_documents.py`

## agent 補助

- `scripts/agent_tools/bootstrap_agent_run.py`
- `scripts/agent_tools/validate_role_write_scope.py`
- `scripts/agent_tools/worktree_scope_lint.py`
- `scripts/agent_tools/worktree_start.py`

## 例外運用

- `scripts/setup_worktree.sh`
- `scripts/worktree_start.sh`
- `scripts/tools/create_worktree.sh`
- `scripts/push_origin.sh`

これらは branch/worktree を使う特別な場合だけ使います。
