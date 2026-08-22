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

for path in docker .github/workflows; do
  if grep -REn --exclude=check_zero_build_contract.sh \
      -e 'devcontainer' -e 'post-create' -e '--mount' -e 'docker-compose' \
      "$path"; then
    fail "$path:development-container-or-mount-reference"
  fi
done

contains docker/Dockerfile 'FROM ubuntu:22.04@sha256:'
contains docker/Dockerfile 'AS cpu-runtime'
contains docker/Dockerfile 'FROM cpu-runtime AS gpu-runtime'
contains docker/Dockerfile 'FROM cpu-runtime AS default-runtime'
contains docker/Dockerfile 'ARG PROJECT_UID=1000'
contains docker/Dockerfile 'ARG PROJECT_GID=1000'
contains docker/Dockerfile 'USER project'
contains docker/Dockerfile 'PYTHON_VERSION=3.11.15'
contains docker/Dockerfile 'COPY --chown=project:project . /workspace/project-template'
contains docker/Dockerfile 'WORKDIR /workspace/project-template'
contains docker/Dockerfile 'COPY docker/requirements-test.txt /tmp/project-test-requirements.txt'
contains docker/requirements-test.txt 'pytest==9.1.1'
contains test/testlist.toml 'format = "parent-test-list-v1"'
contains test/testlist.toml 'environment_owner = "invocation-environment"'
contains docker/Dockerfile 'PROJECT_TEST_ENVIRONMENT_OWNER=project-container'
contains test/testlist.toml 'responsibility = "parent-repository"'
contains .github/workflows/ci.yml 'docker build --platform linux/amd64'
contains .github/workflows/ci.yml 'project-template:ci test/testrunner.sh'
contains .github/workflows/ci.yml 'docker image rm project-template:ci || true'
contains docker/cold-build-smoke.sh 'docker run --rm --platform linux/amd64'
contains docker/cold-build-smoke.sh 'test/testrunner.sh'

printf 'DOCKER_CONTRACT=pass\n'
