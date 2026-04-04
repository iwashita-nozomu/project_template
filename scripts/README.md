# scripts

`scripts/` は、開発、review、文書整備、実験運用を補助する実行入口です。
テンプレートとして残すべき共通スクリプトだけをここから辿れるようにします。

## よく使うもの

### 共通

- [guide.sh](/mnt/l/workspace/project_template/scripts/guide.sh)
  - 入口確認に使います。
- [ci/run_all_checks.sh](/mnt/l/workspace/project_template/scripts/ci/run_all_checks.sh)
  - 主要なチェックをまとめて実行します。
- [run_comprehensive_review.sh](/mnt/l/workspace/project_template/scripts/run_comprehensive_review.sh)
  - repo 全体の確認用です。

### Python を使う場合

- [run_pytest_with_logs.sh](/mnt/l/workspace/project_template/scripts/run_pytest_with_logs.sh)
  - pytest をログ付きで実行します。

### ドキュメント整備

- [tools/check_markdown_lint.py](/mnt/l/workspace/project_template/scripts/tools/check_markdown_lint.py)
- [tools/audit_and_fix_links.py](/mnt/l/workspace/project_template/scripts/tools/audit_and_fix_links.py)
- [tools/fix_markdown_docs.py](/mnt/l/workspace/project_template/scripts/tools/fix_markdown_docs.py)
- [tools/find_similar_documents.py](/mnt/l/workspace/project_template/scripts/tools/find_similar_documents.py)

### agent 補助

- [agent_tools/bootstrap_agent_run.py](/mnt/l/workspace/project_template/scripts/agent_tools/bootstrap_agent_run.py)
- [agent_tools/validate_role_write_scope.py](/mnt/l/workspace/project_template/scripts/agent_tools/validate_role_write_scope.py)

## よく使うコマンド

```bash
make ci-quick
make ci
bash scripts/run_comprehensive_review.sh
python3 scripts/tools/check_markdown_lint.py documents
python3 scripts/tools/audit_and_fix_links.py documents
```

## 実行環境

- shell スクリプトは `python3` を優先します。
- Python 依存を使う場合は `docker/` 側の定義を更新します。
- repo 全体の入口は言語非限定ですが、Python 用補助スクリプトは `python/` 構成を前提にしています。

## 参照先

- [README.md](/mnt/l/workspace/project_template/README.md)
- [QUICK_START.md](/mnt/l/workspace/project_template/QUICK_START.md)
- [documents/WORKFLOW_INVENTORY.md](/mnt/l/workspace/project_template/documents/WORKFLOW_INVENTORY.md)
- [agents/README.md](/mnt/l/workspace/project_template/agents/README.md)
