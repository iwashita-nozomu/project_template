#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
image_tag=project-template:test
pull=0
no_cache=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag) [[ $# -ge 2 ]] || { echo "--tag requires a value" >&2; exit 2; }; image_tag="$2"; shift 2 ;;
    --tag=*) image_tag="${1#*=}"; shift ;;
    --pull) pull=1; shift ;;
    --no-cache) no_cache=1; shift ;;
    -h|--help) echo "usage: $0 [--tag IMAGE] [--pull] [--no-cache]"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

command -v docker >/dev/null 2>&1 || { echo "docker is required" >&2; exit 2; }
if docker image inspect "$image_tag" >/dev/null 2>&1; then
  echo "refusing to overwrite pre-existing image: $image_tag" >&2
  exit 1
fi

cleanup() {
  if docker image inspect "$image_tag" >/dev/null 2>&1; then
    docker image rm "$image_tag" >/dev/null
  fi
}
trap cleanup EXIT HUP INT TERM

build=(docker build --platform linux/amd64 --tag "$image_tag" \
  --file "$repo_root/docker/Dockerfile")
[[ $pull -eq 0 ]] || build+=(--pull)
[[ $no_cache -eq 0 ]] || build+=(--no-cache)
build+=("$repo_root")

printf 'project-test-build:'; printf ' %q' "${build[@]}"; printf '\n'
bash "$repo_root/test/testrunner.sh" --phase static
"${build[@]}"
docker run --rm --platform linux/amd64 \
  "$image_tag" test/testrunner.sh --phase portable
