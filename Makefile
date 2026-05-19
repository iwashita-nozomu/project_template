# @dependency-start
# responsibility Defines template make targets for validation, setup, and agent workflow automation.
# upstream implementation tools/agent_tools/evaluate_agent_run.py exposes agent-evaluate target
# upstream implementation tools/agent_tools/task_close.py enforces closeout gates
# upstream implementation tools/agent_tools/run_repo_dependency_review.sh exposes repo-wide dependency review
# upstream implementation tools/agent_tools/review_backlog_scan.sh exposes integrated review backlog scans
# @dependency-end

.PHONY: ci ci-quick check-matrix docs-check clean-generated github-workflow-check dev-setup tools-help agent-checks agent-surface-checks agent-canon-check agent-canon-latest-check agent-canon-links agent-canon-status agent-canon-ensure-latest agent-canon-rebuild-tools agent-canon-update-plan agent-canon-latest agent-canon-update agent-canon-merge-main agent-canon-pr-check docker-check python-env-status python-env-prepare docker-build-check docker-build-check-host-docker docker-run devcontainer-render server-check experiment-check docker-shell docker-jupyter docker-codex docker-codex-host-docker fresh-clone-check template-check start-repository task-start doc-start task-close agent-evaluate dependency-review dependency-review-surfaces review-backlog-scan waterfall-gate-check user-preference-log

# ★推奨: 統合 CI（pytest + pyright + ruff）
ci:
	bash tools/ci/run_all_checks.sh

# CI 高速モード（ruff skip）
ci-quick:
	bash tools/ci/run_all_checks.sh --quick

# changed-path / profile based check selector
check-matrix:
	@echo "Check matrix:"
	@echo "  docs-only:        make docs-check && dependency header checks for changed docs"
	@echo "  Python changes:   targeted pytest + python3 -m pyright + python3 -m ruff check python tests --select D,E,F,I,UP"
	@echo "  AgentCanon/root:  make agent-canon-pr-check or make agent-surface-checks"
	@echo "  Docker/runtime:   make docker-check [and make docker-build-check if build behavior changed]"
	@echo "  GitHub/Copilot:   make github-workflow-check"
	@echo "  Experiment:       make experiment-check"
	@echo "  Full confidence:  make ci"

# template fresh clone acceptance
fresh-clone-check:
	bash tools/ci/check_fresh_clone.sh

# higher-level template acceptance
template-check: fresh-clone-check

# clone-time repository bootstrap
start-repository:
	bash scripts/start_repository.sh $(ARGS)

# machine-driven task start
task-start:
	python3 tools/agent_tools/task_start.py $(ARGS)

# machine-driven document start
doc-start:
	python3 tools/agent_tools/doc_start.py $(ARGS)

# machine-driven task close gate
task-close:
	python3 tools/agent_tools/task_close.py $(ARGS)

# machine-driven agent behavior evaluation
agent-evaluate:
	python3 tools/agent_tools/evaluate_agent_run.py $(ARGS)

# machine-driven repo-wide dependency review
dependency-review:
	bash tools/agent_tools/run_repo_dependency_review.sh $(ARGS)

# strict dependency review for both template root views and AgentCanon source
dependency-review-surfaces:
	bash tools/agent_tools/run_repo_dependency_review.sh --fail-missing $(ARGS)
	bash tools/agent_tools/run_repo_dependency_review.sh --root vendor/agent-canon --fail-missing $(ARGS)

# integrated file-by-file review backlog scan
review-backlog-scan:
	bash tools/agent_tools/review_backlog_scan.sh $(ARGS)

# machine-driven intermediate waterfall gate check
waterfall-gate-check:
	python3 tools/agent_tools/waterfall_gate_check.py $(ARGS)

# machine-driven user preference note append
user-preference-log:
	python3 tools/agent_tools/log_user_preference.py $(ARGS)

# repo-wide Markdown lint / link checks
docs-check:
	bash tools/ci/run_docs_checks.sh

# remove generated, ignored artifacts that make the template workspace noisy
clean-generated:
	git clean -Xdf .pytest_cache .ruff_cache build logs reports tests/logs .devcontainer/docker-compose.generated.yml

# GitHub Actions / PR template / Copilot convention checks
github-workflow-check:
	python3 tools/ci/check_github_workflows.py

# agent runtime / skill drift checks
agent-checks:
	$(MAKE) agent-surface-checks

agent-surface-checks:
	bash tools/ci/check_agent_canon_latest.sh
	bash tools/sync_agent_canon.sh check
	python3 tools/docs/mirror_skill_shims.py --target .claude/skills --prune --check
	python3 tools/agent_tools/check_agent_runtime_alignment.py
	python3 tools/agent_tools/smoke_test_research_perspective_pack.py

# read-only gate for upstream agent-canon freshness
agent-canon-latest-check:
	bash tools/ci/check_agent_canon_latest.sh

# shared surface drift only
agent-canon-check:
	bash tools/sync_agent_canon.sh check

# root shared surface を vendor 正本へ再リンク
agent-canon-links:
	bash tools/sync_agent_canon.sh link-root

# submodule pin / legacy tree 設定を確認
agent-canon-status:
	bash tools/sync_agent_canon.sh status

# upstream agent-canon を task 開始時に取り込む
agent-canon-ensure-latest:
	bash tools/update_agent_canon.sh latest $(ARGS)

agent-canon-rebuild-tools:
	bash tools/update_agent_canon.sh rebuild-tools

agent-canon-update-plan:
	bash tools/update_agent_canon.sh plan $(ARGS)

agent-canon-latest:
	bash tools/update_agent_canon.sh latest $(ARGS)

agent-canon-update:
	bash tools/update_agent_canon.sh latest $(ARGS)

agent-canon-merge-main:
	bash tools/update_agent_canon.sh merge-main-into-current $(ARGS)

# shared canon 専用の PR gate
agent-canon-pr-check:
	bash tools/ci/check_agent_canon_pr.sh

# Dockerfile と requirements の整合
docker-check:
	bash tools/docker_dependency_validator.sh

# 現在の runtime で repo-local .venv が許可されるかを表示
python-env-status:
	python3 tools/ci/python_env_policy.py

# 許可される runtime で canonical .venv を準備
python-env-prepare:
	python3 tools/ci/python_env_policy.py --create

# Docker イメージ build / smoke 可否の確認
docker-build-check:
	bash docker/check_build.sh --pack docker/packs/default.toml

# Docker socket を mount した build smoke check
docker-build-check-host-docker:
	bash docker/check_build.sh --pack docker/packs/default-host-docker.toml

# 任意 program を canonical container で実行
docker-run:
	python3 tools/ci/run_repo_program.py $(ARGS)

# devcontainer compose を canonical pack から生成
devcontainer-render:
	bash .devcontainer/generate-runtime-compose.sh

# main server host readiness
server-check:
	python3 tools/ci/check_server_readiness.py --layout vendor/agent-canon/documents/templates/server_runtime_layout.template.toml

# experiment registry validation
experiment-check:
	python3 tools/ci/check_experiment_registry.py

# 既定 pack の shell を起動
docker-shell:
	python3 tools/ci/run_in_repo_container.py --pack docker/packs/default.toml --shell-session --tty

# canonical container で JupyterLab を起動
docker-jupyter:
	python3 tools/ci/run_in_repo_container.py --pack docker/packs/default.toml --keep-image --port $${JUPYTER_HOST_PORT:-8888}:8888 -- jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --ServerApp.token="$${JUPYTER_TOKEN:-project-template}"

# nested Codex を既定 pack で起動
docker-codex:
	python3 tools/ci/run_codex_in_repo_container.py

# nested Codex を host Docker socket 付き pack で起動
docker-codex-host-docker:
	python3 tools/ci/run_codex_in_repo_container.py --profile host-docker

# 開発開始の確認
dev-setup:
	@echo "Template clone is ready. Read documents/template-bootstrap.md, then run: make fresh-clone-check"

# ツール情報表示
tools-help:
	@echo "=== Tool entrypoints ==="
	@echo ""
	@echo "Start with: make check-matrix"
	@echo "Detailed catalog: python3 tools/agent_tools/tool_catalog.py --format markdown"
