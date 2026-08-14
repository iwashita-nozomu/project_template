#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
image_tag=project-template:zero-build-cold-smoke
pull=0
no_cache=0
expect_non_default_id=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pull) pull=1; shift ;;
    --no-cache) no_cache=1; shift ;;
    --expect-non-default-id) expect_non_default_id=1; shift ;;
    --tag) [[ $# -ge 2 ]] || { echo "--tag requires a value" >&2; exit 2; }; image_tag="$2"; shift 2 ;;
    --tag=*) image_tag="${1#*=}"; shift ;;
    -h|--help) echo "usage: $0 --pull --no-cache [--expect-non-default-id] [--tag IMAGE]"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

[[ $pull -eq 1 ]] || { echo "cold acceptance requires --pull" >&2; exit 2; }
[[ $no_cache -eq 1 ]] || { echo "cold acceptance requires --no-cache" >&2; exit 2; }
command -v docker >/dev/null 2>&1 || { echo "docker is required" >&2; exit 2; }

project_uid="$(id -u)"
project_gid="$(id -g)"
[[ "$project_uid" =~ ^[1-9][0-9]*$ ]] || { echo "host UID must be positive" >&2; exit 2; }
[[ "$project_gid" =~ ^[1-9][0-9]*$ ]] || { echo "host GID must be positive" >&2; exit 2; }
if [[ $expect_non_default_id -eq 1 && "$project_uid:$project_gid" == 1000:1000 ]]; then
  echo "expected a non-default runner UID/GID" >&2
  exit 2
fi

build=(docker build --platform linux/amd64 --pull --no-cache \
  --build-arg "PROJECT_UID=$project_uid" --build-arg "PROJECT_GID=$project_gid" \
  --tag "$image_tag" --file "$repo_root/docker/Dockerfile" "$repo_root")
printf 'cold-build:'; printf ' %q' "${build[@]}"; printf '\n'
"${build[@]}"

smoke=$(cat <<'SMOKE'
set -euo pipefail
cd /workspace/project-template

test "$(id -un)" = project
test "$(id -u)" = "${EXPECTED_UID:?}"
test "$(id -g)" = "${EXPECTED_GID:?}"
test "$HOME" = /home/project
sudo -n true
bash docker/install_python_dependencies.sh "$PWD"
bash .devcontainer/post-create-parent.sh "$PWD"
python3 tools/check_runtime_independence.py
python3 tools/check_markdown_links.py
python3 tools/check_github_workflows.py
make cpp-test
python3 -c 'import jax; assert jax.default_backend() == "cpu"'
! command -v nvcc
printf 'COLD_SMOKE=pass uid=%s gid=%s\n' "$(id -u)" "$(id -g)"
SMOKE
)

docker run --rm --platform linux/amd64 \
  --mount "type=bind,src=$repo_root,dst=/workspace/project-template" \
  --workdir /workspace/project-template \
  --env "EXPECTED_UID=$project_uid" \
  --env "EXPECTED_GID=$project_gid" \
  "$image_tag" /bin/bash -lc "$smoke"
