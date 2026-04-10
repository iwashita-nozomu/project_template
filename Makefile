.PHONY: ci ci-quick docs-check dev-setup tools-help agent-checks agent-canon-check agent-canon-links agent-canon-snapshot agent-canon-status agent-canon-pr-check docker-check docker-build-check docker-build-check-host-docker docker-run devcontainer-render server-check experiment-check docker-shell docker-codex docker-codex-host-docker fresh-clone-check template-check task-start doc-start task-close user-preference-log

# ★推奨: 統合 CI（pytest + pyright + ruff）
ci:
	bash tools/ci/run_all_checks.sh

# CI 高速モード（ruff skip）
ci-quick:
	bash tools/ci/run_all_checks.sh --quick

# template fresh clone acceptance
fresh-clone-check:
	bash tools/ci/check_fresh_clone.sh

# higher-level template acceptance
template-check: fresh-clone-check

# machine-driven task start
task-start:
	python3 tools/agent_tools/task_start.py $(ARGS)

# machine-driven document start
doc-start:
	python3 tools/agent_tools/doc_start.py $(ARGS)

# machine-driven task close gate
task-close:
	python3 tools/agent_tools/task_close.py $(ARGS)

# machine-driven user preference note append
user-preference-log:
	python3 tools/agent_tools/log_user_preference.py $(ARGS)

# repo-wide Markdown lint / link checks
docs-check:
	bash tools/ci/run_docs_checks.sh

# agent runtime / skill drift checks
agent-checks:
	bash tools/sync_agent_canon.sh check
	python3 tools/docs/mirror_skill_shims.py --target .claude/skills --prune --check
	python3 tools/agent_tools/check_agent_runtime_alignment.py
	python3 tools/agent_tools/smoke_test_research_perspective_pack.py

# shared surface drift only
agent-canon-check:
	bash tools/sync_agent_canon.sh check

# root shared surface を vendor 正本へ再リンク
agent-canon-links:
	bash tools/sync_agent_canon.sh link-root

# backward-compatible alias
agent-canon-snapshot:
	bash tools/sync_agent_canon.sh snapshot

# subtree / snapshot 設定を確認
agent-canon-status:
	bash tools/sync_agent_canon.sh status

# shared canon 専用の PR gate
agent-canon-pr-check:
	bash tools/ci/check_agent_canon_pr.sh

# Dockerfile と requirements の整合
docker-check:
	bash tools/docker_dependency_validator.sh

# Docker イメージ build 可否の確認
docker-build-check:
	bash tools/ci/check_docker_build.sh --pack docker/packs/default.toml

# Docker socket を mount した build smoke check
docker-build-check-host-docker:
	bash tools/ci/check_docker_build.sh --pack docker/packs/default-host-docker.toml

# 任意 program を canonical container で実行
docker-run:
	python3 tools/ci/run_repo_program.py $(ARGS)

# devcontainer compose を canonical pack から生成
devcontainer-render:
	python3 tools/ci/render_devcontainer_compose.py --pack docker/packs/default.toml --output .devcontainer/docker-compose.generated.yml

# main server host readiness
server-check:
	python3 tools/ci/check_server_readiness.py --layout documents/templates/server_runtime_layout.template.toml

# experiment registry validation
experiment-check:
	python3 tools/ci/check_experiment_registry.py

# 既定 pack の shell を起動
docker-shell:
	python3 tools/ci/run_in_repo_container.py --pack docker/packs/default.toml --shell-session --tty

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
	@echo "=== Available Tools & Scripts ==="
	@echo ""
	@cat tools/README.md | head -40
