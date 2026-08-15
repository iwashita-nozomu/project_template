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

forbidden='vendor/agent-canon|tools/agent-canon|AGENT_CANON_|agent_canon_source_root|checkout_agent_canon_submodule|\.agent-canon/docker-compose.generated.yml'
if grep -REn --exclude=check_zero_build_contract.sh "$forbidden" docker .devcontainer .github/workflows; then
  fail 'live-runtime-reference'
fi

contains docker/Dockerfile 'FROM --platform=linux/amd64 ubuntu:22.04@sha256:'
contains docker/Dockerfile 'AS cpu-runtime'
contains docker/Dockerfile 'FROM cpu-runtime AS gpu-runtime'
contains docker/Dockerfile 'FROM cpu-runtime AS default-runtime'
contains docker/Dockerfile 'ARG PROJECT_UID=1000'
contains docker/Dockerfile 'ARG PROJECT_GID=1000'
contains docker/Dockerfile 'USER project'
contains docker/Dockerfile 'PYTHON_VERSION=3.11.15'
contains .devcontainer/devcontainer.json '"dockerfile": "../docker/Dockerfile"'
contains .devcontainer/devcontainer.json '"target": "default-runtime"'
contains .devcontainer/devcontainer.json '.devcontainer/post-create-parent.sh'
contains .github/workflows/docker-build.yml 'bash docker/cold-build-smoke.sh --pull --no-cache --expect-non-default-id'

if grep -Eq 'initializeCommand|dockerComposeFile|postAttachCommand' .devcontainer/devcontainer.json; then
  fail '.devcontainer/devcontainer.json:generated-or-mutable-lifecycle-forbidden'
fi
if grep -Eq 'pip[[:space:]]+install|apt-get|npm[[:space:]]+install|venv' .devcontainer/post-create-parent.sh; then
  fail '.devcontainer/post-create-parent.sh:environment-mutation-forbidden'
fi

python3 - <<'PY'
import json
from pathlib import Path
payload = json.loads(Path('.devcontainer/devcontainer.json').read_text(encoding='utf-8'))
assert payload['build']['dockerfile'] == '../docker/Dockerfile'
assert payload['build']['target'] == 'default-runtime'
assert payload['containerUser'] == 'project'
assert payload['remoteUser'] == 'project'
PY

printf 'DOCKER_CONTRACT=pass\n'
