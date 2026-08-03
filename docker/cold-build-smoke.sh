#!/usr/bin/env bash
# @dependency-start
# contract test
# responsibility Performs the single cold parent-image build and single non-root runtime smoke.
# upstream design ../documents/design/docker-zero-build-environment.md cold acceptance owner and runtime evidence
# upstream environment ./Dockerfile direct Ubuntu 22.04 image and runtime identity
# upstream implementation ../vendor/agent-canon/.devcontainer/post-create-entrypoint.sh shared-first lifecycle resolver
# @dependency-end

set -euo pipefail

# Output contract: build and smoke diagnostics remain on stdout, followed by one
# JSON pass receipt containing status, uid, gid, home, and workspace. CI consumes
# this stdout receipt; it is not a checked-in source dependency or artifact path.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
image_tag="project-template:zero-build-cold-smoke"
pull=0
no_cache=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --pull)
      pull=1
      shift
      ;;
    --no-cache)
      no_cache=1
      shift
      ;;
    --tag)
      [ "$#" -ge 2 ] || { echo "--tag requires a value" >&2; exit 2; }
      image_tag="$2"
      shift 2
      ;;
    --tag=*)
      image_tag="${1#*=}"
      shift
      ;;
    -h|--help)
      printf 'usage: %s --pull --no-cache [--tag IMAGE]\n' "$0"
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      exit 2
      ;;
  esac
done

[ "$pull" -eq 1 ] || { echo "cold acceptance requires --pull" >&2; exit 2; }
[ "$no_cache" -eq 1 ] || { echo "cold acceptance requires --no-cache" >&2; exit 2; }
command -v docker >/dev/null 2>&1 || { echo "docker is required" >&2; exit 2; }

project_uid="$(id -u)"
project_gid="$(id -g)"
case "$project_uid" in ''|0|*[!0-9]*) echo "host UID must be positive" >&2; exit 2 ;; esac
case "$project_gid" in ''|0|*[!0-9]*) echo "host GID must be positive" >&2; exit 2 ;; esac

build_command=(
  docker build
  --platform linux/amd64
  --pull
  --no-cache
  --build-arg "PROJECT_UID=${project_uid}"
  --build-arg "PROJECT_GID=${project_gid}"
  --tag "$image_tag"
  --file "$repo_root/docker/Dockerfile"
  "$repo_root"
)
printf 'cold-build:'
printf ' %q' "${build_command[@]}"
printf '\n'
"${build_command[@]}"

smoke_script=$(cat <<'SMOKE'
set -euo pipefail
workspace=/workspace/project_template
cd "$workspace"

# The lifecycle is deliberately reached through the same public resolver used by
# devcontainer.json, so standalone and vendored source-root behavior are tested.
python3 tools/agent-canon/agent_tools/agent_canon_source_root.py exec \
  .devcontainer/post-create-entrypoint.sh "$workspace"

test "$(id -u)" -ne 0
test "$(id -un)" = project
test "${HOME:-}" = /home/project
test "$(stat -c '%u:%g' "$HOME")" = "$(id -u):$(id -g)"
sudo -n true
test -w "$workspace"
test -f "$HOME/.zshrc"
test -z "${ZDOTDIR:-}"
test ! -e /etc/project-template/zsh/.zshenv
zsh -fc 'test "$SHELL" = /bin/zsh; exit 0'

python3 --version | grep -E '^Python 3\.11\.'
python3 -m pip --version
python3 -c 'import jax; print("JAX_RUNTIME=" + jax.__version__)'
nvcc --version | grep -F 'release 12.8'
dpkg-query -W -f='${Version}\n' cuda-toolkit-12-8 | grep -Fx '12.8.2-1'
dpkg-query -W -f='${Version}\n' libcudnn9-cuda-12 | grep -Fx '9.8.0.87-1'
dpkg-query -W -f='${Version}\n' libcudnn9-dev-cuda-12 | grep -Fx '9.8.0.87-1'
dpkg-query -W -f='${Version}\n' libnccl2 | grep -Fx '2.25.1-1+cuda12.8'
dpkg-query -W -f='${Version}\n' libnccl-dev | grep -Fx '2.25.1-1+cuda12.8'

node --version | grep -Fx 'v22.14.0'
npm --version | grep -Fx '10.9.2'
ninja --version
tree --version
git --version
cmake --version
ssh -V
docker --version
dot -V
jq --version
gh --version
agent-canon --version

printf '{"status":"pass","uid":%s,"gid":%s,"home":"%s","workspace":"%s"}\n' \
  "$(id -u)" "$(id -g)" "$HOME" "$workspace"
SMOKE
)

run_command=(
  docker run --rm --platform linux/amd64
  --mount "type=bind,src=${repo_root},dst=/workspace/project_template"
  --workdir /workspace/project_template
  --env AGENT_CANON_CONTAINER_USER=project
  --env AGENT_CANON_DEPENDENCY_PROFILE=full
  "$image_tag"
  /bin/bash -lc "$smoke_script"
)
printf 'cold-smoke:'
printf ' %q' "${run_command[@]}"
printf '\n'
"${run_command[@]}"
