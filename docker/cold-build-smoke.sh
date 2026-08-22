#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
image_tag=project-template:zero-build-cold-smoke
pull=0
no_cache=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --pull) pull=1; shift ;;
    --no-cache) no_cache=1; shift ;;
    --tag) [[ $# -ge 2 ]] || { echo "--tag requires a value" >&2; exit 2; }; image_tag="$2"; shift 2 ;;
    --tag=*) image_tag="${1#*=}"; shift ;;
    -h|--help) echo "usage: $0 --pull --no-cache [--tag IMAGE]"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
done

[[ $pull -eq 1 ]] || { echo "cold acceptance requires --pull" >&2; exit 2; }
[[ $no_cache -eq 1 ]] || { echo "cold acceptance requires --no-cache" >&2; exit 2; }
command -v docker >/dev/null 2>&1 || { echo "docker is required" >&2; exit 2; }

build=(docker build --platform linux/amd64 --pull --no-cache \
  --tag "$image_tag" --file "$repo_root/docker/Dockerfile" "$repo_root")
printf 'cold-build:'; printf ' %q' "${build[@]}"; printf '\n'
"${build[@]}"

docker run --rm --platform linux/amd64 \
  "$image_tag" test/testrunner.sh
