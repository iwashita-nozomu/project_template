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
jax_util_ref="${JAX_UTIL_REF:-c3d2d649d7f8435fbe997bd7c0e9095c46ac7b18}"
jax_util_local_repo="${JAX_UTIL_LOCAL_REPO:-/mnt/git/jax_util.git}"
jax_util_remote_repo="${JAX_UTIL_REMOTE_REPO:-git+ssh://git@github.com/iwashita-nozomu/jax_utils.git}"

if [ ! -f "$requirements" ]; then
  echo "docker/requirements.txt not found: $requirements" >&2
  exit 1
fi

mkdir -p "$state_dir"

if [ -d "$jax_util_local_repo" ]; then
  git config --global --add safe.directory "$jax_util_local_repo" || true
  jax_util_spec="git+file://${jax_util_local_repo}@${jax_util_ref}"
else
  jax_util_spec="${jax_util_remote_repo}@${jax_util_ref}"
fi

current_hash="$(
  {
    sha256sum "$requirements"
    printf '%s\n' "$jax_util_spec"
  } | sha256sum | awk '{print $1}'
)"

jax_util_import_ok() {
  python3 - <<'PY'
from jax_util.base import Vector

_ = Vector
PY
}

if [ -f "$hash_file" ] && [ "$(cat "$hash_file")" = "$current_hash" ]; then
  if jax_util_import_ok && python3 -m pip check; then
    exit 0
  fi
fi

python3 -m pip install --upgrade pip
python3 -m pip install --no-cache-dir -r "$requirements"
python3 -m pip install --no-cache-dir --force-reinstall --no-deps "$jax_util_spec"
jax_util_import_ok
python3 -m pip check
printf '%s\n' "$current_hash" > "$hash_file"
