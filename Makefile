PROJECT_ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHON ?= /opt/project-venv/bin/python
DOCKER ?= docker
DOCKER_IMAGE ?= project-template:local
CPP_PROFILE ?= dev
CPP_BUILD_DIR ?= $(PROJECT_ROOT)/build/cpp/$(CPP_PROFILE)
CPP_INSTALL_DIR ?= $(PROJECT_ROOT)/.state/cpp-install/$(CPP_PROFILE)
export PYTHONPATH := $(PROJECT_ROOT)/python:$(PROJECT_ROOT)

.PHONY: image-precondition test test-local lint-local typing-local package-build-local
.PHONY: ci ci-quick pr-check validation-core-local full-check-local check-matrix
.PHONY: docs-check docs-check-local github-workflow-check github-workflow-check-local
.PHONY: runtime-independence-check runtime-independence-check-local
.PHONY: base-project-check-local docker-check docker-contract-check-local image-smoke-local
.PHONY: fresh-clone-check fresh-clone-check-local start-repository
.PHONY: docker-build-check docker-cold-check docker-run docker-shell
.PHONY: cpp-configure cpp-build cpp-test cpp-test-local cpp-install cpp-experiments
.PHONY: dev-setup tools-help clean-generated

image-precondition:
	@test "$${PROJECT_TEMPLATE_IMAGE:-}" = 1 || { \
	  echo 'validation must run in docker/Dockerfile target cpu-dev (Dev Container or docker run)' >&2; \
	  exit 2; \
	}
	@test -x "$(PYTHON)" || { echo 'image-owned Python is missing: $(PYTHON)' >&2; exit 2; }

runtime-independence-check-local: image-precondition
	$(PYTHON) tools/check_runtime_independence.py

runtime-independence-check: runtime-independence-check-local

docs-check-local: image-precondition
	$(PYTHON) tools/check_markdown_links.py

docs-check: docs-check-local

github-workflow-check-local: image-precondition
	$(PYTHON) tools/check_github_workflows.py

github-workflow-check: github-workflow-check-local

lint-local: image-precondition
	$(PYTHON) -m ruff check python tests/tools tools

typing-local: image-precondition
	pyright

package-build-local: image-precondition
	rm -rf .state/dist
	$(PYTHON) -m build --wheel --no-isolation --outdir .state/dist

test-local: image-precondition
	$(PYTHON) -m pytest -q tests/tools

test: test-local

base-project-check-local: runtime-independence-check-local lint-local typing-local package-build-local test-local

cpp-configure: image-precondition
	cmake -S cpp -B "$(CPP_BUILD_DIR)" -DCMAKE_INSTALL_PREFIX="$(CPP_INSTALL_DIR)"

cpp-build: cpp-configure
	cmake --build "$(CPP_BUILD_DIR)" --parallel

cpp-test-local: cpp-build
	ctest --test-dir "$(CPP_BUILD_DIR)" --output-on-failure

cpp-test: cpp-test-local

cpp-install: cpp-build
	cmake --install "$(CPP_BUILD_DIR)"

cpp-experiments: cpp-configure
	cmake --build "$(CPP_BUILD_DIR)" --target cpp-experiments --parallel

docker-contract-check-local: image-precondition
	$(PYTHON) tools/check_environment_contract.py

docker-check: docker-contract-check-local

fresh-clone-check-local: image-precondition
	bash tools/check_fresh_clone.sh

fresh-clone-check: fresh-clone-check-local

validation-core-local: docs-check-local base-project-check-local cpp-test-local github-workflow-check-local docker-contract-check-local

full-check-local: validation-core-local fresh-clone-check-local

pr-check: full-check-local

ci: full-check-local

ci-quick: validation-core-local

image-smoke-local: image-precondition
	test "$$(id -un)" = project
	test "$$(id -u)" -ne 0
	test "$${HOME}" = /home/project
	test "$$(stat -c %u /opt/project-venv)" = 0
	test ! -w /opt/project-venv
	$(PYTHON) -m pip check
	$(PYTHON) -c 'import jax; assert jax.default_backend() == "cpu"'
	python3 --version | grep -F '3.11.15'
	node --version | grep -F 'v22.14.0'
	codex --version | grep -F '0.145.0'
	pyright --version | grep -F '1.1.411'
	bash-language-server --version | grep -F '5.6.0'
	test -r /usr/local/share/project-template/image-manifest.txt

check-matrix:
	@$(PYTHON) tools/validation_routing.py describe 2>/dev/null || python3 tools/validation_routing.py describe

start-repository:
	bash scripts/start_repository.sh $(ARGS)

docker-build-check:
	$(DOCKER) build --platform linux/amd64 \
	  --build-arg "PROJECT_UID=$$(id -u)" \
	  --build-arg "PROJECT_GID=$$(id -g)" \
	  --target cpu-validation --tag $(DOCKER_IMAGE) --file docker/Dockerfile .

docker-cold-check:
	bash docker/cold-build-smoke.sh --pull --no-cache --tag $(DOCKER_IMAGE)

docker-run:
	$(DOCKER) run --rm --platform linux/amd64 $(DOCKER_IMAGE) $(ARGS)

docker-shell:
	$(DOCKER) run --rm -it --platform linux/amd64 \
	  --mount "type=bind,src=$(PROJECT_ROOT),dst=/workspace/project" \
	  --workdir /workspace/project \
	  --env PROJECT_TEMPLATE_IMAGE=1 \
	  $(DOCKER_IMAGE) /bin/zsh

clean-generated:
	git clean -Xdf .pytest_cache .ruff_cache .state build logs reports

dev-setup:
	@echo 'Build/reopen the Dev Container, then run make pr-check. No post-create installation is required.'

tools-help: check-matrix
