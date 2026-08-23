#!/usr/bin/env bash
set -euo pipefail

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
exec "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)/run-tests.sh" \
  --pull --no-cache --tag "$image_tag"
