#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

fail() {
  printf 'DOCKER_CONTRACT_FINDING=%s\n' "$1" >&2
  exit 1
}

contains() {
  local path="$1" needle="$2"
  grep -Fq -- "$needle" "$path" || fail "$path:missing:$needle"
}

if [[ -d .devcontainer ]]; then
  fail '.devcontainer-must-not-exist'
fi
[[ -x docker/run-tests.sh ]] || fail 'docker/run-tests.sh:not-executable'

contains docker/Dockerfile 'FROM ubuntu:22.04@sha256:'
contains docker/Dockerfile 'AS project-base'
contains docker/Dockerfile 'FROM project-base AS full-runtime'
contains docker/Dockerfile 'FROM project-base AS gpu-runtime'
contains docker/Dockerfile 'FROM project-base AS default-runtime'
contains docker/Dockerfile 'ARG PROJECT_UID='
contains docker/Dockerfile 'ARG PROJECT_GID='
contains docker/Dockerfile 'USER project'
contains docker/Dockerfile 'PYTHON_VERSION='
contains docker/Dockerfile 'COPY --chown=project:project . /workspace/project-template'
contains docker/Dockerfile 'WORKDIR /workspace/project-template'
contains docker/Dockerfile 'COPY docker/requirements-test.txt /tmp/project-test-requirements.txt'
contains docker/Dockerfile 'install_python_dependencies.sh /workspace/project-template --profile full'
contains docker/Dockerfile 'install_python_dependencies.sh /workspace/project-template --profile gpu'
contains docker/requirements-test.txt 'pytest=='
contains test/testlist.toml 'format = "parent-test-list-v1"'
contains test/testlist.toml 'environment_owner = "invocation-environment"'
contains docker/Dockerfile 'PROJECT_TEST_ENVIRONMENT_OWNER=project-container'
contains test/testlist.toml 'responsibility = "parent-repository"'
contains .github/workflows/ci.yml 'bash docker/run-tests.sh --tag project-template:ci'
contains docker/run-tests.sh 'docker build --platform linux/amd64'
contains docker/run-tests.sh 'docker run --rm --platform linux/amd64'
contains docker/run-tests.sh 'docker image rm "$image_tag"'
contains docker/cold-build-smoke.sh 'run-tests.sh'

printf 'DOCKER_CONTRACT=pass\n'
