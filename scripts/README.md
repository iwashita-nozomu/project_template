# scripts

`scripts/` は、開発、review、文書整備、実験運用を補助する実行入口です。
テンプレートとして残すべき共通スクリプトだけをここから辿れるようにします。

## よく使うもの

### 共通

- [guide.sh](/mnt/l/workspace/project_template/scripts/guide.sh)
  - 入口確認に使います。
- [ci/run_all_checks.sh](/mnt/l/workspace/project_template/scripts/ci/run_all_checks.sh)
  - 主要なチェックをまとめて実行します。
- [ci/run_docs_checks.sh](/mnt/l/workspace/project_template/scripts/ci/run_docs_checks.sh)
  - repo-wide の Markdown 体裁とリンクを確認します。
- [ci/check_docker_build.sh](/mnt/l/workspace/project_template/scripts/ci/check_docker_build.sh)
  - `docker/Dockerfile` の build 可否、`docker` CLI、run-time `safe.directory` 設定を確認します。
- [ci/run_container_pack.py](/mnt/l/workspace/project_template/scripts/ci/run_container_pack.py)
  - repo 定義の runtime pack を build / smoke します。
- [ci/run_in_repo_container.py](/mnt/l/workspace/project_template/scripts/ci/run_in_repo_container.py)
  - repo workspace を mount した container command を実行します。
- [ci/run_python_in_dockerfile.py](/mnt/l/workspace/project_template/scripts/ci/run_python_in_dockerfile.py)
  - Python file を rule ベースで container 実行します。
- [ci/run_codex_in_repo_container.py](/mnt/l/workspace/project_template/scripts/ci/run_codex_in_repo_container.py)
  - nested Codex を canonical container 内で起動します。
- [ci/check_server_readiness.py](/mnt/l/workspace/project_template/scripts/ci/check_server_readiness.py)
  - main server host の path、mount、builder、Docker socket readiness を確認します。
- [ci/check_experiment_registry.py](/mnt/l/workspace/project_template/scripts/ci/check_experiment_registry.py)
  - `experiments/registry.toml` の topic entry と command surface を確認します。
- [run_comprehensive_review.sh](/mnt/l/workspace/project_template/scripts/run_comprehensive_review.sh)
  - repo 全体の確認用です。

### Python

- [run_pytest_with_logs.sh](/mnt/l/workspace/project_template/scripts/run_pytest_with_logs.sh)
  - pytest をログ付きで実行します。

### 実験運用

- [experiments/create_experiment_topic.py](/mnt/l/workspace/project_template/scripts/experiments/create_experiment_topic.py)
  - `_template/` から topic と registry entry を作ります。
- [experiments/sync_experiment_registry_context.py](/mnt/l/workspace/project_template/scripts/experiments/sync_experiment_registry_context.py)
  - branch / worktree / scope file を registry metadata に同期します。
- [experiments/run_managed_experiment.py](/mnt/l/workspace/project_template/scripts/experiments/run_managed_experiment.py)
  - server 上の実験 run で `result/<run_name>/`、`run_manifest.json`、`run.log`、report stub を初期化します。

ベースライン依存:
- `psutil`
  - process / memory / CPU の観測に使います。
- `pipdeptree`
  - install 済み依存の tree と衝突確認に使います。
- `deptry`
  - import と依存定義のズレ確認に使います。
- `snakeviz`
  - `cProfile` の可視化に使います。

### ドキュメント整備

- [tools/check_markdown_lint.py](/mnt/l/workspace/project_template/scripts/tools/check_markdown_lint.py)
- [tools/check_markdown_math.py](/mnt/l/workspace/project_template/scripts/tools/check_markdown_math.py)
- [tools/audit_and_fix_links.py](/mnt/l/workspace/project_template/scripts/tools/audit_and_fix_links.py)
- [tools/fix_markdown_docs.py](/mnt/l/workspace/project_template/scripts/tools/fix_markdown_docs.py)
- [tools/find_similar_documents.py](/mnt/l/workspace/project_template/scripts/tools/find_similar_documents.py)
- [tools/mirror_skill_shims.py](/mnt/l/workspace/project_template/scripts/tools/mirror_skill_shims.py)
  - `.agents/skills/` から runtime 用 mirror を同期します。

### agent 補助

- [agent_tools/bootstrap_agent_run.py](/mnt/l/workspace/project_template/scripts/agent_tools/bootstrap_agent_run.py)
- [agent_tools/validate_role_write_scope.py](/mnt/l/workspace/project_template/scripts/agent_tools/validate_role_write_scope.py)
- [agent_tools/smoke_test_research_perspective_pack.py](/mnt/l/workspace/project_template/scripts/agent_tools/smoke_test_research_perspective_pack.py)
  - research perspective review pack の runtime と bundle を smoke test します。
- [agent_tools/worktree_scope_lint.py](/mnt/l/workspace/project_template/scripts/agent_tools/worktree_scope_lint.py)
  - `WORKTREE_SCOPE.md` の placeholder と drift を確認します。
- [agent_tools/worktree_start.py](/mnt/l/workspace/project_template/scripts/agent_tools/worktree_start.py)
  - worktree kickoff summary を出します。
- [worktree_start.sh](/mnt/l/workspace/project_template/scripts/worktree_start.sh)
  - worktree kickoff の user-facing 入口です。
- [sync_agent_canon.sh](/mnt/l/workspace/project_template/scripts/sync_agent_canon.sh)
  - `vendor/agent-canon/` subtree の add / pull / push / status をまとめます。
- [push_origin.sh](/mnt/l/workspace/project_template/scripts/push_origin.sh)
  - commit 後の canonical push 入口です。

## よく使うコマンド

```bash
make agent-checks
make ci-quick
make ci
make docs-check
make docker-build-check
make docker-build-check-host-docker
make server-check
make experiment-check
make docker-shell
make docker-codex
make docker-codex-host-docker
bash scripts/run_comprehensive_review.sh
python3 -m pyright
python3 -m pytest python/tests/ -q --tb=short
python3 -m ruff check python/ --select D,E,F,I,UP
pipdeptree --warn fail
deptry python
python3 scripts/ci/run_container_pack.py --pack docker/packs/default.toml --print-only
python3 scripts/ci/run_codex_in_repo_container.py --print-only
python3 scripts/ci/check_server_readiness.py
python3 scripts/tools/mirror_skill_shims.py --target .claude/skills --prune
python3 scripts/agent_tools/smoke_test_research_perspective_pack.py
bash scripts/sync_agent_canon.sh status
python3 scripts/ci/check_experiment_registry.py
python3 scripts/experiments/create_experiment_topic.py my_topic
python3 scripts/experiments/sync_experiment_registry_context.py --topic my_topic --branch work/my-topic-YYYYMMDD
python3 scripts/experiments/run_managed_experiment.py --topic _template --use-registered-command smoke --dry-run
```

## 実行環境

- shell スクリプトは `python3` を優先します。
- Python 依存を使う場合は `docker/` 側の定義を更新します。
- この template は Python 実装と Markdown 文書を前提にしています。

## 参照先

- [README.md](/mnt/l/workspace/project_template/README.md)
- [QUICK_START.md](/mnt/l/workspace/project_template/QUICK_START.md)
- [documents/WORKFLOW_INVENTORY.md](/mnt/l/workspace/project_template/documents/WORKFLOW_INVENTORY.md)
- [agents/README.md](/mnt/l/workspace/project_template/agents/README.md)
