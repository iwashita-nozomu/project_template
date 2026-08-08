#!/usr/bin/env bash
# @dependency-start
# contract test
# responsibility Performs the single cold parent-image build and single non-root runtime smoke.
# upstream design ../documents/design/docker-zero-build-environment.md cold acceptance owner and runtime evidence
# upstream environment ./Dockerfile direct Ubuntu 22.04 image and runtime identity
# upstream implementation ../vendor/agent-canon/.devcontainer/post-create-entrypoint.sh shared-first lifecycle resolver
# @dependency-end

set -euo pipefail

# Output contract: build and smoke diagnostics remain on stdout, followed by a
# container identity readback and one host-side JSON pass receipt. CI consumes
# these stdout receipts; they are not checked-in source dependencies or artifact
# paths. This witness is rootful only. Rootless/user-namespace mapping is a
# separate documented contract.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
image_tag="project-template:zero-build-cold-smoke"
pull=0
no_cache=0
expect_non_default_id=0

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
    --expect-non-default-id)
      expect_non_default_id=1
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
      printf 'usage: %s --pull --no-cache [--expect-non-default-id] [--tag IMAGE]\n' "$0"
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
docker_security_options="$(docker info --format '{{json .SecurityOptions}}' 2>/dev/null || true)"
case "$docker_security_options" in
  *rootless*)
    echo "rootless Docker is outside the rootful cold-smoke contract" >&2
    exit 2
    ;;
esac

project_uid="$(id -u)"
project_gid="$(id -g)"
case "$project_uid" in ''|0|*[!0-9]*) echo "host UID must be positive" >&2; exit 2 ;; esac
case "$project_gid" in ''|0|*[!0-9]*) echo "host GID must be positive" >&2; exit 2 ;; esac
if [ "$expect_non_default_id" -eq 1 ]; then
  if [ "$project_uid:$project_gid" = "1000:1000" ]; then
    echo "cold acceptance requires a non-default host UID/GID when --expect-non-default-id is set" >&2
    exit 2
  fi
  printf 'COLD_SMOKE_EXPECT_NON_DEFAULT_ID=pass uid=%s gid=%s\n' "$project_uid" "$project_gid"
fi

probe_relative=".devcontainer/.cold-build-smoke-${project_uid}-${project_gid}-$$"
probe_host="$repo_root/$probe_relative"
[ ! -e "$probe_host" ] || { echo "smoke probe already exists: $probe_host" >&2; exit 2; }
cleanup_probe() {
  rm -f -- "$probe_host"
}
trap cleanup_probe EXIT HUP INT TERM

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
# The fixed bootstrap owns Node/npm and Ninja. Install that language-runtime
# layer explicitly before the shared entrypoint exercises its fail-closed check.
python3 tools/agent-canon/agent_tools/agent_canon_source_root.py exec \
  .devcontainer/bootstrap-dependencies.sh --install-language-runtime
python3 tools/agent-canon/agent_tools/agent_canon_source_root.py exec \
  .devcontainer/post-create-entrypoint.sh "$workspace"

test "$(id -u)" -ne 0
test "$(id -un)" = project
test "$(id -u)" = "${EXPECTED_EXECUTOR_UID:?}"
test "$(id -g)" = "${EXPECTED_EXECUTOR_GID:?}"
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
python3 -c 'import jax; assert jax.default_backend() == "cpu"; print("JAX_RUNTIME=" + jax.__version__)'
! command -v nvcc
! dpkg-query -W cuda-toolkit-12-8
! dpkg-query -W libcudnn9-cuda-12
! dpkg-query -W libcudnn9-dev-cuda-12
! dpkg-query -W libnccl2
! dpkg-query -W libnccl-dev

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

probe_relative="${SMOKE_PROBE_RELATIVE:?}"
case "$probe_relative" in
  .devcontainer/.cold-build-smoke-[1-9][0-9]*-[1-9][0-9]*-[1-9][0-9]*) ;;
  *) echo "invalid smoke probe path" >&2; exit 1 ;;
esac
probe_path="$workspace/$probe_relative"
printf 'container_uid=%s\ncontainer_gid=%s\nexecutor_uid=%s\nexecutor_gid=%s\n' \
  "$(id -u)" "$(id -g)" "$EXPECTED_EXECUTOR_UID" "$EXPECTED_EXECUTOR_GID" >"$probe_path"
test -f "$probe_path"

printf 'COLD_SMOKE_CONTAINER_READBACK=identity contract=rootful container_uid=%s container_gid=%s executor_uid=%s executor_gid=%s home=%s workspace=%s bind_probe=%s\n' \
  "$(id -u)" "$(id -g)" "$EXPECTED_EXECUTOR_UID" "$EXPECTED_EXECUTOR_GID" \
  "$HOME" "$workspace" "$probe_path"
SMOKE
)

run_command=(
  docker run --rm --platform linux/amd64
  --mount "type=bind,src=${repo_root},dst=/workspace/project_template"
  --workdir /workspace/project_template
  --env AGENT_CANON_CONTAINER_USER=project
  --env AGENT_CANON_DEPENDENCY_PROFILE=full
  --env "EXPECTED_EXECUTOR_UID=${project_uid}"
  --env "EXPECTED_EXECUTOR_GID=${project_gid}"
  --env "SMOKE_PROBE_RELATIVE=${probe_relative}"
  "$image_tag"
  /bin/bash -lc "$smoke_script"
)
printf 'cold-smoke:'
printf ' %q' "${run_command[@]}"
printf '\n'
"${run_command[@]}"

probe_content="$(cat -- "$probe_host")"
container_uid="$(printf '%s\n' "$probe_content" | awk -F= '$1 == "container_uid" {print $2; exit}')"
container_gid="$(printf '%s\n' "$probe_content" | awk -F= '$1 == "container_gid" {print $2; exit}')"
generated_uid="$(printf '%s\n' "$probe_content" | awk -F= '$1 == "executor_uid" {print $2; exit}')"
generated_gid="$(printf '%s\n' "$probe_content" | awk -F= '$1 == "executor_gid" {print $2; exit}')"
host_probe_uid="$(stat -c '%u' "$probe_host")"
host_probe_gid="$(stat -c '%g' "$probe_host")"
test "$container_uid" = "$project_uid"
test "$container_gid" = "$project_gid"
test "$generated_uid" = "$project_uid"
test "$generated_gid" = "$project_gid"
test "$host_probe_uid" = "$project_uid"
test "$host_probe_gid" = "$project_gid"
printf 'COLD_SMOKE_BIND_READBACK=pass contract=rootful host_path=%s host_uid=%s host_gid=%s generated_uid=%s generated_gid=%s container_uid=%s container_gid=%s\n' \
  "$probe_host" "$host_probe_uid" "$host_probe_gid" "$generated_uid" "$generated_gid" "$container_uid" "$container_gid"
printf '{"status":"pass","contract":"rootful","identity":{"host_executor_uid":%s,"host_executor_gid":%s,"generated_project_uid":%s,"generated_project_gid":%s,"container_uid":%s,"container_gid":%s},"bind_readback":{"host_path":"%s","host_uid":%s,"host_gid":%s,"container_path":"/workspace/project_template/%s"}}\n' \
  "$project_uid" "$project_gid" "$generated_uid" "$generated_gid" "$container_uid" "$container_gid" \
  "$probe_host" "$host_probe_uid" "$host_probe_gid" "$probe_relative"
