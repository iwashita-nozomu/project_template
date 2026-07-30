#!/usr/bin/env bash
# @dependency-start
# contract environment
# responsibility Builds and smoke-tests the base image and validates the projected devcontainer wrappers.
# upstream environment Dockerfile canonical container image definition
# upstream environment packs/default.toml default runtime pack metadata
# upstream environment ../.dockerignore excludes AgentCanon from image build context
# upstream design ../vendor/agent-canon/CONTAINER_OPERATIONS.md AgentCanon container and devcontainer operation rulebook
# downstream implementation ../.github/workflows/docker-build.yml uses this submodule-aware build gate
# @dependency-end

set -euo pipefail

pack="docker/packs/default.toml"
builder="${DOCKER_BUILDER:-docker}"
tag=""
pull=0
skip_run=0
keep_image=0
print_only=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --pack)
      pack="$2"
      shift 2
      ;;
    --builder)
      builder="$2"
      shift 2
      ;;
    --tag)
      tag="$2"
      shift 2
      ;;
    --pull)
      pull=1
      shift
      ;;
    --skip-run)
      skip_run=1
      shift
      ;;
    --keep-image)
      keep_image=1
      shift
      ;;
    --print-only)
      print_only=1
      shift
      ;;
    *)
      printf 'unknown argument: %s\n' "$1" >&2
      exit 2
      ;;
  esac
done

if [ ! -f "$pack" ]; then
  printf 'pack not found: %s\n' "$pack" >&2
  exit 2
fi

mapfile -t pack_values < <(
  python3 - "$pack" <<'PY'
from __future__ import annotations

import sys
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

with open(sys.argv[1], "rb") as handle:
    data = tomllib.load(handle)
pack = data["pack"]
runtime = data.get("runtime", {})
mounts = runtime.get("mounts", [])
print(pack["dockerfile"])
print(pack["context"])
print(pack["image_tag"])
print(runtime.get("workdir", "/workspace"))
print("1" if any("/var/run/docker.sock" in mount for mount in mounts) else "0")
PY
)

dockerfile="${pack_values[0]}"
context="${pack_values[1]}"
default_tag="${pack_values[2]}"
workdir="${pack_values[3]}"
mount_docker_sock="${pack_values[4]}"
tag="${tag:-$default_tag}"

build_command=("$builder" build -f "$dockerfile" -t "$tag")
if [ "$pull" -eq 1 ]; then
  build_command+=(--pull)
fi
build_command+=("$context")

if [ "$mount_docker_sock" = "1" ]; then
  smoke_script='set -euo pipefail
python3 --version
docker version'
else
smoke_script='set -euo pipefail
python3 --version
python3 -m pip --version
cmake --version
ninja --version
ssh -V
docker --version
dot -V
for script in \
  vendor/agent-canon/.devcontainer/bootstrap-shared-runtime.sh \
  vendor/agent-canon/.devcontainer/finalize-shared-runtime.sh \
  vendor/agent-canon/.devcontainer/generate-runtime-compose.sh \
  vendor/agent-canon/.devcontainer/post-attach.sh \
  vendor/agent-canon/.devcontainer/post-create.sh \
  .devcontainer/post-create-parent.sh; do
  bash -n "$script"
done
test -x vendor/agent-canon/.devcontainer/finalize-shared-runtime.sh
printf "devcontainer lifecycle smoke deferred to managed compose and fresh-clone checks\n"
ROOT="$(pwd)"
cmake -S "$ROOT/cpp" -B "$ROOT/build/cpp/docker-smoke" \
  -DCMAKE_INSTALL_PREFIX="$ROOT/.state/cpp-install/docker-smoke"
cmake --build "$ROOT/build/cpp/docker-smoke" --parallel
ctest --test-dir "$ROOT/build/cpp/docker-smoke" --output-on-failure
cmake --install "$ROOT/build/cpp/docker-smoke"
bash docker/register_safe_directories.sh "$ROOT"'
fi

run_command=("$builder" run --rm -v "$PWD:/workspace" -w "$workdir")
if [ -d /mnt/git ]; then
  run_command+=(-v /mnt/git:/mnt/git)
fi
if [ "$mount_docker_sock" = "1" ] && [ -S /var/run/docker.sock ]; then
  run_command+=(-v /var/run/docker.sock:/var/run/docker.sock)
fi
run_command+=("$tag" /bin/bash -lc "$smoke_script")

printf 'build:\n'
printf '%q ' "${build_command[@]}"
printf '\n'
if [ "$skip_run" -eq 0 ]; then
  printf 'smoke:\n'
  printf '%q ' "${run_command[@]}"
  printf '\n'
fi

if [ "$print_only" -eq 1 ]; then
  exit 0
fi

"${build_command[@]}"
if [ "$skip_run" -eq 0 ]; then
  "${run_command[@]}"
fi

if [ "$keep_image" -eq 0 ]; then
  "$builder" image rm -f "$tag" >/dev/null 2>&1 || true
fi
