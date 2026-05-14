#!/usr/bin/env bash
# @dependency-start
# responsibility Installs repo Python dependencies after the workspace is mounted.
# upstream design ../vendor/agent-canon/CONTAINER_OPERATIONS.md keeps workspace-dependent packages out of image build.
# upstream implementation requirements.txt declares the repo Python dependency contract.
# downstream implementation ../vendor/agent-canon/.devcontainer/post-create.sh calls this installer.
# @dependency-end

set -euo pipefail

workspace="${1:-/workspace}"
requirements="${workspace%/}/docker/requirements.txt"
state_dir="${workspace%/}/.state/docker"
hash_file="${state_dir}/requirements.sha256"

if [ ! -f "$requirements" ]; then
  echo "docker/requirements.txt not found: $requirements" >&2
  exit 1
fi

mkdir -p "$state_dir"
current_hash="$(sha256sum "$requirements" | awk '{print $1}')"

if [ -f "$hash_file" ] && [ "$(cat "$hash_file")" = "$current_hash" ]; then
  python3 -m pip check
  exit 0
fi

python3 -m pip install --upgrade pip
python3 -m pip install --no-cache-dir -r "$requirements"
python3 -m pip check
printf '%s\n' "$current_hash" > "$hash_file"
