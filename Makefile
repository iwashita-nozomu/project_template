# @dependency-start
# contract configuration
# responsibility Defines template make targets for validation, setup, and agent workflow automation.
# upstream implementation tools/agent-canon/ci/run_container_pack.py runs Docker runtime packs
# @dependency-end

PYTHON ?= python3

CI_TOOLS := tools/agent-canon/ci
AGENT_CANON_DISPATCH := env PYTHONPATH="vendor/agent-canon/tools:tools$${PYTHONPATH:+:$${PYTHONPATH}}" $(PYTHON) -m agent_tools.agent_canon_source_root exec

DOCKER_DEFAULT_PACK ?= docker/packs/default.toml
DOCKER_HOST_PACK ?= docker/packs/default-host-docker.toml
# AgentCanon source template; a parent may override this variable explicitly.
SERVER_LAYOUT ?= vendor/agent-canon/templates/documents/server_runtime_layout.template.toml
CPP_PROFILE ?= dev
CPP_BUILD_DIR ?= build/cpp/$(CPP_PROFILE)
CPP_INSTALL_DIR ?= .state/cpp-install/$(CPP_PROFILE)
REPO_WIDE_REVIEW_REPORT_DIR ?= reports/agents/repo-wide-review-check
REPO_WIDE_REVIEW_QUERY ?= repo-wide review runtime surface stale path check

.PHONY: ci ci-quick pr-check check-matrix docs-check clean-generated github-workflow-check
.PHONY: fresh-clone-check dev-setup tools-help
.PHONY: start-repository
.PHONY: agent-canon agent-canon-check agent-canon-latest-check agent-canon-update
.PHONY: agent-canon-pr-check
.PHONY: docker-check python-env-status python-env-prepare
.PHONY: docker-build-check docker-build-check-host-docker docker-run devcontainer-render
.PHONY: server-check experiment-check docker-shell docker-jupyter docker-codex docker-codex-host-docker
.PHONY: cpp-configure cpp-build cpp-test cpp-install cpp-experiments

# Validation targets
# Full confidence gate: agent/runtime, docs, Rust, container, pytest, pyright,
# pydocstyle, and ruff. Run on main/manual integration, not every PR.
ci:
	bash tools/agent-canon/ci/run_all_checks.sh

# Broad local gate with ruff skipped; still runs the other full-confidence surfaces.
ci-quick:
	bash tools/agent-canon/ci/run_all_checks.sh --quick

# Template-owned PR baseline. Repository-machinery tests stay in the full integration gate.
pr-check:
	$(MAKE) docs-check
	$(MAKE) github-workflow-check
	$(MAKE) cpp-test

# Human-readable validation catalog; this is not a second routing classifier.
check-matrix:
	@echo "Check matrix:"
	@echo "  ordinary PR:     make pr-check"
	@echo "  docs-only:       make docs-check"
	@echo "  Python project changes: targeted project tests/type/lint once project Python exists"
	@echo "  C++ changes:     make cpp-test"
	@echo "  AgentCanon source:   make agent-canon-pr-check"
	@echo "  AgentCanon shared views: make agent-canon-check"
	@echo "  AgentCanon update: make agent-canon-update"
	@echo "  Docker/runtime:  make docker-check [and make docker-build-check if image/runtime behavior changed]"
	@echo "  GitHub automation: make github-workflow-check"
	@echo "  Experiment:      make experiment-check"
	@echo "  main/manual full confidence: make ci"

# template fresh clone acceptance
fresh-clone-check:
	bash tools/agent-canon/ci/check_fresh_clone.sh

# Agent workflow targets
# clone-time repository bootstrap
start-repository:
	bash scripts/start_repository.sh $(ARGS)

# Documentation and generated artifacts
# repo-wide Markdown lint / link checks
docs-check:
	tools/agent-canon/bin/agent-canon docs check

# remove generated, ignored artifacts that make the template workspace noisy
clean-generated:
	git clean -Xdf \
		.pytest_cache \
		.ruff_cache \
		build \
		logs \
		reports \
		tests/logs \
		.agent-canon/docker-compose.generated.yml

# GitHub and agent-runtime targets
# GitHub Actions / PR template convention checks
github-workflow-check:
	$(PYTHON) $(CI_TOOLS)/check_github_workflows.py

# AgentCanon sync/update targets
# read-only gate for upstream agent-canon freshness
agent-canon-latest-check:
	$(AGENT_CANON_DISPATCH) tools/ci/check_agent_canon_latest.sh

# shared surface drift only
agent-canon-check:
	$(AGENT_CANON_DISPATCH) tools/sync_agent_canon.sh check

# upstream agent-canon を task 開始時に取り込む
agent-canon-update:
	$(AGENT_CANON_DISPATCH) tools/update_agent_canon.sh latest $(ARGS)

agent-canon:
	$(AGENT_CANON_DISPATCH) $(ARGS)

# shared canon 専用の PR gate
agent-canon-pr-check:
	$(AGENT_CANON_DISPATCH) tools/ci/check_agent_canon_pr.sh

# Docker and runtime targets
# Dockerfile と requirements の整合
docker-check:
	bash tools/agent-canon/docker_dependency_validator.sh

# 現在の runtime で repo-local .venv が許可されるかを表示
python-env-status:
	$(PYTHON) $(CI_TOOLS)/python_env_policy.py

# 許可される runtime で canonical .venv を準備
python-env-prepare:
	$(PYTHON) $(CI_TOOLS)/python_env_policy.py --create

# Docker イメージ build / smoke 可否の確認
docker-build-check:
	$(PYTHON) $(CI_TOOLS)/run_container_pack.py --pack $(DOCKER_DEFAULT_PACK)

# Docker socket を mount した build smoke check
docker-build-check-host-docker:
	$(PYTHON) $(CI_TOOLS)/run_container_pack.py --pack $(DOCKER_HOST_PACK)

# 任意 program を canonical container で実行
docker-run:
	$(PYTHON) $(CI_TOOLS)/run_repo_program.py $(ARGS)

# devcontainer compose を canonical pack から生成
devcontainer-render:
	AGENT_CANON_DEVCONTAINER_REPO_ROOT=. AGENT_CANON_DOCKER_COMPOSE_OUTPUT=.agent-canon/docker-compose.generated.yml \
	bash vendor/agent-canon/.devcontainer/generate-runtime-compose.sh

# main server host readiness
server-check:
	$(PYTHON) $(CI_TOOLS)/check_server_readiness.py --layout $(SERVER_LAYOUT)

# experiment registry validation
experiment-check:
	$(PYTHON) $(CI_TOOLS)/check_experiment_registry.py

# C++ project entrypoint and profile-scoped artifact commands
cpp-configure:
	cmake -S cpp -B "$(CPP_BUILD_DIR)" -DCMAKE_INSTALL_PREFIX="$(CPP_INSTALL_DIR)"

cpp-build: cpp-configure
	cmake --build "$(CPP_BUILD_DIR)" --parallel

cpp-test: cpp-build
	ctest --test-dir "$(CPP_BUILD_DIR)" --output-on-failure

cpp-install: cpp-build
	cmake --install "$(CPP_BUILD_DIR)"

cpp-experiments: cpp-configure
	cmake --build "$(CPP_BUILD_DIR)" --target cpp-experiments --parallel

# Help targets
# 開発開始の確認
dev-setup:
	@echo "Template clone is ready. Read documents/contracts/template-bootstrap.md, then run: make fresh-clone-check"

# ツール情報表示
tools-help:
	@echo "Core targets:"
	@echo "  make pr-check            Run the Template-owned pull-request baseline"
	@echo "  make check-matrix        Show validation routing"
	@echo "  make ci-quick            Run broad local validation"
	@echo "  make docs-check          Run Markdown/document checks"
	@echo "  make agent-canon         Dispatch a canonical agent-canon source command"
	@echo "  make docker-check        Check Docker dependency boundaries"
	@echo "  make cpp-build           Configure and build the C++ profile"
	@echo "  make cpp-test            Configure/build, then run CTest"
	@echo "  make cpp-install         Configure/build, then install artifacts"
	@echo "  make cpp-experiments     Build native experiment targets"
	@echo ""
	@echo "Detailed catalog:"
	@echo "  make agent-canon ARGS='tools/agent_tools/tool_catalog.py --format markdown'"
