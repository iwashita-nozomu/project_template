PYTHON ?= python3
DOCKER ?= docker
DOCKER_IMAGE ?= project-template:local
CPP_PROFILE ?= dev
CPP_BUILD_DIR ?= build/$(CPP_PROFILE)
CPP_INSTALL_DIR ?= .state/install/$(CPP_PROFILE)

.PHONY: test ci ci-quick pr-check check-matrix docs-check github-workflow-check
.PHONY: runtime-independence-check fresh-clone-check start-repository
.PHONY: docker-check docker-test docker-run docker-shell
.PHONY: cpp-configure cpp-build cpp-test cpp-install
.PHONY: dev-setup tools-help clean-generated

runtime-independence-check:
	$(PYTHON) tools/check_runtime_independence.py

docs-check:
	$(PYTHON) tools/check_markdown_links.py

github-workflow-check:
	$(PYTHON) tools/check_github_workflows.py

test:
	bash test/testrunner.sh

pr-check: runtime-independence-check docs-check github-workflow-check test

ci: runtime-independence-check docs-check github-workflow-check docker-check docker-test

ci-quick: runtime-independence-check docs-check github-workflow-check cpp-test

check-matrix:
	@printf '%s\n' \
	  'ordinary PR:        make pr-check' \
	  'bootstrap/tree:      make fresh-clone-check' \
	  'Docker/runtime:      make docker-check && make docker-test' \
	  'C++:                 make cpp-test' \
	  'full host gate:      make ci'

fresh-clone-check:
	bash tools/check_fresh_clone.sh

start-repository:
	bash scripts/start_repository.sh $(ARGS)

docker-check:
	bash docker/check_zero_build_contract.sh

docker-test:
	bash docker/run-tests.sh --tag $(DOCKER_IMAGE)

docker-run:
	$(DOCKER) run --rm --platform linux/amd64 $(DOCKER_IMAGE) $(ARGS)

docker-shell:
	$(DOCKER) run --rm -it --platform linux/amd64 $(DOCKER_IMAGE) /bin/zsh

cpp-configure:
	cmake -S . -B "$(CPP_BUILD_DIR)" -DCMAKE_INSTALL_PREFIX="$(CPP_INSTALL_DIR)"

cpp-build: cpp-configure
	cmake --build "$(CPP_BUILD_DIR)" --parallel

cpp-test: cpp-build
	ctest --test-dir "$(CPP_BUILD_DIR)" --output-on-failure

cpp-install: cpp-build
	cmake --install "$(CPP_BUILD_DIR)"

clean-generated:
	git clean -Xdf .pytest_cache .ruff_cache .state build dist logs reports test/logs experiments/_template

dev-setup:
	@echo 'Clone is complete. Read documents/contracts/template-bootstrap.md, then run make pr-check.'

tools-help: check-matrix
