# ツール入口

このディレクトリは、repo で使う補助ツールの入口です。
詳細な台帳ではなく、いま残すべき実行導線だけを整理します。

agent/worktree helper のうち shared canon に属するものは `vendor/agent-canon/` が正本です。
ownership と validation は [SHARED_RUNTIME_SURFACES.md](/mnt/l/workspace/project_template/documents/SHARED_RUNTIME_SURFACES.md) を参照し、この文書では product 側の実行入口だけを案内します。

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
- `scripts/ci/check_server_readiness.py`
  - main server host の readiness を確認します。
- `scripts/ci/check_experiment_registry.py`
  - experiment registry の entrypoint と command を確認します。
- `scripts/experiments/create_experiment_topic.py`
  - experiment topic を scaffold します。
- `scripts/experiments/sync_experiment_registry_context.py`
  - registry の branch / worktree metadata を同期します。
- `scripts/experiments/run_managed_experiment.py`
  - server 上の実験 run artifact を初期化します。
- `scripts/run_comprehensive_review.sh`
  - repo 全体の確認をまとめて実行します。
- `scripts/run_pytest_with_logs.sh`
  - Python テストをログ付きで実行します。
- `scripts/tools/check_markdown_lint.py`
  - Markdown の体裁確認です。
- `scripts/tools/audit_and_fix_links.py`
  - Markdown のリンク監査です。
- `scripts/worktree_start.sh`
  - worktree kickoff の user-facing 入口です。
- `scripts/sync_agent_canon.sh`
  - shared agent canon surface の drift check と再同期です。
- `scripts/push_origin.sh`
  - commit 後の canonical push 入口です。

## 補足

- `setup_worktree.sh` などの branch/worktree 補助は例外運用用です。
- 既定運用は `main` であり、通常作業の入口にはしません。

## 参照先

- [scripts/README.md](/mnt/l/workspace/project_template/scripts/README.md)
- [SHARED_RUNTIME_SURFACES.md](/mnt/l/workspace/project_template/documents/SHARED_RUNTIME_SURFACES.md)
- [TOOLS_DIRECTORY.md](/mnt/l/workspace/project_template/documents/tools/TOOLS_DIRECTORY.md)
