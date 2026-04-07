.PHONY: git_init ci ci-quick docs-check dev-setup tools-help agent-checks agent-canon-links agent-canon-snapshot agent-canon-status docker-check docker-build-check docker-build-check-host-docker server-check experiment-check docker-shell docker-codex docker-codex-host-docker

# Git 初期化（初回のみ）
git_init:
	bash scripts/git_init.sh
	@echo "✅ Git setup complete"

# ★推奨: 統合 CI（pytest + pyright + ruff）
ci:
	bash scripts/ci/run_all_checks.sh

# CI 高速モード（ruff skip）
ci-quick:
	bash scripts/ci/run_all_checks.sh --quick

# repo-wide Markdown lint / link checks
docs-check:
	bash scripts/ci/run_docs_checks.sh

# agent runtime / skill drift checks
agent-checks:
	python3 scripts/tools/mirror_skill_shims.py --target .claude/skills --prune --check
	python3 scripts/agent_tools/smoke_test_research_perspective_pack.py

# root shared surface を vendor 正本へ再リンク
agent-canon-links:
	bash scripts/sync_agent_canon.sh link-root

# backward-compatible alias
agent-canon-snapshot:
	bash scripts/sync_agent_canon.sh snapshot

# subtree / snapshot 設定を確認
agent-canon-status:
	bash scripts/sync_agent_canon.sh status

# Dockerfile と requirements の整合
docker-check:
	python3 scripts/docker_dependency_validator.py

# Docker イメージ build 可否の確認
docker-build-check:
	bash scripts/ci/check_docker_build.sh --pack docker/packs/default.toml

# Docker socket を mount した build smoke check
docker-build-check-host-docker:
	bash scripts/ci/check_docker_build.sh --pack docker/packs/default-host-docker.toml

# main server host readiness
server-check:
	python3 scripts/ci/check_server_readiness.py --layout documents/templates/server_runtime_layout.template.toml

# experiment registry validation
experiment-check:
	python3 scripts/ci/check_experiment_registry.py

# 既定 pack の shell を起動
docker-shell:
	python3 scripts/ci/run_in_repo_container.py --pack docker/packs/default.toml --shell-session --tty

# nested Codex を既定 pack で起動
docker-codex:
	python3 scripts/ci/run_codex_in_repo_container.py

# nested Codex を host Docker socket 付き pack で起動
docker-codex-host-docker:
	python3 scripts/ci/run_codex_in_repo_container.py --profile host-docker

# 開発環境初期化
dev-setup: git_init
	@echo "✅ Dev environment ready. Start with: make ci-quick"

# ツール情報表示
tools-help:
	@echo "=== Available Tools & Scripts ==="
	@echo ""
	@cat scripts/README.md | head -40
