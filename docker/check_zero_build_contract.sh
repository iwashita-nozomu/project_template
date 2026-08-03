#!/usr/bin/env bash
# @dependency-start
# contract tool
# responsibility Performs static/readback validation of the parent zero-build ownership and host-mount contract.
# upstream design ../documents/design/docker-zero-build-environment.md runtime order, ownership, and audit packet
# upstream environment ./Dockerfile product image construction
# upstream environment ./packs/default.toml default isolated runtime pack
# downstream implementation ./cold-build-smoke.sh executes the one runtime acceptance witness
# @dependency-end

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

fail() {
  printf 'ZERO_BUILD_CONTRACT_FINDING=%s\n' "$1" >&2
  exit 1
}

contains() {
  local path="$1"
  local needle="$2"
  grep -Fq -- "$needle" "$path" || fail "${path#./}:missing:${needle}"
}

dockerfile=docker/Dockerfile
pack=docker/packs/default.toml
workflow=.github/workflows/docker-build.yml
design=documents/design/docker-zero-build-environment.md

contains "$dockerfile" 'FROM --platform=linux/amd64 ubuntu:22.04@sha256:0d779ea97881505f5ef0039336ee85edba27519bdba968c284c86ee066a973c8'
if grep -Eiq '^[[:space:]]*FROM[[:space:]].*nvidia/cuda|cuda-drivers|nvidia-driver|nvidia-kernel' "$dockerfile"; then
  fail 'docker/Dockerfile:driver-base-or-package-forbidden'
fi
contains "$dockerfile" 'cuda-keyring_1.1-1_all.deb'
contains "$dockerfile" 'd93190d50b98ad4699ff40f4f7af50f16a76dac3bb8da1eaaf366d47898ff8df'
contains "$dockerfile" 'cuda-toolkit-12-8=12.8.2-1'
contains "$dockerfile" 'libcudnn9-cuda-12=9.8.0.87-1'
contains "$dockerfile" 'libcudnn9-dev-cuda-12=9.8.0.87-1'
contains "$dockerfile" 'libnccl2=2.25.1-1+cuda12.8'
contains "$dockerfile" 'libnccl-dev=2.25.1-1+cuda12.8'
contains "$dockerfile" 'PYTHON_VERSION=3.11.15'
contains "$dockerfile" 'PYTHON_SHA256=272179ddd9a2e41a0fc8e42e33dfbdca0b3711aa5abf372d3f2d51543d09b625'
contains "$dockerfile" 'ARG PROJECT_USER=project'
contains "$dockerfile" 'case "$PROJECT_USER" in'
contains "$dockerfile" 'groupadd --gid "$PROJECT_GID" "$PROJECT_USER"'
contains "$dockerfile" 'useradd --uid "$PROJECT_UID" --gid "$PROJECT_GID"'
contains "$dockerfile" 'NOPASSWD:ALL'
contains "$dockerfile" 'chmod 0440 "/etc/sudoers.d/$PROJECT_USER"'
contains "$dockerfile" 'visudo --check --file="/etc/sudoers.d/$PROJECT_USER"'
grep -Eq '^USER[[:space:]]+project[[:space:]]*$' "$dockerfile" || fail 'docker/Dockerfile:last-user-is-not-project'
last_instruction="$(grep -E '^(FROM|ARG|ENV|RUN|COPY|WORKDIR|EXPOSE|CMD|USER|ENTRYPOINT)[[:space:]]' "$dockerfile" | tail -1)"
[ "$last_instruction" = 'USER project' ] || fail 'docker/Dockerfile:USER-project-must-be-last-instruction'
if grep -Ev '^[[:space:]]*#' "$dockerfile" | grep -Eq 'ZDOTDIR|\.zshenv|parent-environment\.sh|(^|[[:space:]])(nodejs|npm|ninja-build|tree)([[:space:]]|\\|$)'; then
  fail 'docker/Dockerfile:startup-or-derived-tool-duplicate'
fi

contains "$pack" 'platform = "linux/amd64"'
if grep -Eq '^[[:space:]]*mounts[[:space:]]*=' "$pack"; then
  fail 'docker/packs/default.toml:host-mounts-forbidden'
fi
if grep -Eq '/var/run/docker.sock|/mnt/git|/root/\.config|/root/\.ssh|SSH_AUTH_SOCK|~/.codex|/mnt/agent-canon-secrets' "$pack"; then
  fail 'docker/packs/default.toml:host-file-or-daemon-dependency'
fi

contains docker/codex-container-profiles.toml 'mount_host_gitconfig = false'
contains docker/codex-container-profiles.toml 'mount_host_git_credentials = false'
contains docker/codex-container-profiles.toml 'forward_ssh_auth_sock = false'
contains docker/codex-container-profiles.toml 'forward_env = []'
contains "$workflow" 'bash docker/cold-build-smoke.sh --pull --no-cache'
contains "$workflow" '      - "vendor/agent-canon"'
contains "$workflow" '      - "pyproject.toml"'
workflow_commands="$(grep -Ev '^[[:space:]]*#' "$workflow")"
if printf '%s\n' "$workflow_commands" | grep -Fq 'default-host-docker.toml' \
  || printf '%s\n' "$workflow_commands" | grep -Fq 'run_container_pack.py'; then
  fail '.github/workflows/docker-build.yml:default-must-have-one-cold-route'
fi

contains pyproject.toml '"jax[cuda12-local]"'
contains docker/requirements.txt 'jax==0.10.2'
contains docker/requirements.txt 'jax-cuda12-plugin==0.10.2'
contains docker/requirements.txt 'jax-cuda12-pjrt==0.10.2'
contains docker/requirements.txt 'jaxlib==0.10.2'
contains docker/requirements.txt 'pyyaml==6.0.3'
contains "$design" 'https://hub.docker.com/_/ubuntu'
contains "$design" 'https://docs.nvidia.com/cuda/cuda-installation-guide-linux/#ubuntu'
contains "$design" 'https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/'
contains "$design" 'https://docs.jax.dev/en/latest/installation.html'
contains "$design" 'audit_item_update=recorded'
contains "$design" 'audit_unit=environment-containers'
contains "$design" 'audit_clause_refs=environment-containers.Invariant.1;environment-containers.Invariant.2;environment-containers.Invariant.3;environment-containers.Invariant.4;environment-containers.Invariant.5;environment-containers.Invariant.6;environment-containers.Invariant.7;environment-containers.Invariant.8'
contains "$design" 'audit_readback=reports/parent-audit-projection/audit-receipts.md#environment-containers'
contains "$design" 'audit_runtime_defer_readback=reports/parent-audit-projection/defer-receipts.md#environment-containers'
if grep -Fq 'docker-cold-build-smoke.json' "$design"; then
  fail 'documents/design/docker-zero-build-environment.md:named-cold-receipt-forbidden'
fi
if grep -Fq '/var/run/docker.sock' README.md QUICK_START.md; then
  fail 'reader-docs:default-docker-socket-example-forbidden'
fi
contains README.md 'docker/packs/default-host-docker.toml'
contains QUICK_START.md 'docker/packs/default-host-docker.toml'

[ -L .devcontainer/devcontainer.json ] || fail '.devcontainer/devcontainer.json:must-remain-AgentCanon-view'
[ -x .devcontainer/post-create-parent.sh ] || fail '.devcontainer/post-create-parent.sh:not-executable'
contains .devcontainer/post-create-parent.sh 'sudo -n true'
if grep -Eq '\.zshenv|/root/\.codex|/etc/project-template/parent-environment\.sh' .devcontainer/post-create-parent.sh; then
  fail '.devcontainer/post-create-parent.sh:forbidden-shell-state-dependency'
fi

gitlink="$(git ls-files -s vendor/agent-canon)"
vendor_head="$(git -C vendor/agent-canon rev-parse HEAD)"
printf '%s\n' "$gitlink" | grep -Fq "$vendor_head" || fail 'vendor/agent-canon:index-pin-does-not-match-source-head'
python3 - <<'PY'
import tomllib
from pathlib import Path

for name in ("docker/packs/default.toml", "docker/packs/default-host-docker.toml"):
    with Path(name).open("rb") as stream:
        payload = tomllib.load(stream)
    assert payload["pack"]["platform"] == "linux/amd64", name
PY

printf 'ZERO_BUILD_CONTRACT=pass\n'
