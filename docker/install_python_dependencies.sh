#!/usr/bin/env bash
set -euo pipefail

workspace=/workspace
profile=full
workspace_set=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --profile) [[ $# -ge 2 ]] || { echo "missing value for --profile" >&2; exit 2; }; profile="$2"; shift 2 ;;
    --profile=*) profile="${1#*=}"; shift ;;
    -*) echo "unknown installer option: $1" >&2; exit 2 ;;
    *)
      [[ $workspace_set -eq 0 ]] || { echo "unexpected installer argument: $1" >&2; exit 2; }
      workspace="$1"
      workspace_set=1
      shift
      ;;
  esac
done

project_root="${workspace%/}"
lock_file="$project_root/docker/requirements.txt"
gpu_lock_file="$project_root/docker/requirements-gpu.txt"
project_file="$project_root/pyproject.toml"

[[ -f "$project_file" ]] || { echo "missing project metadata: $project_file" >&2; exit 2; }
[[ -f "$lock_file" ]] || { echo "missing dependency lock: $lock_file" >&2; exit 2; }

case "$profile" in
  full)
    python3 -m pip install --require-hashes -r "$lock_file"
    python3 -m pip install --no-build-isolation --no-deps --editable "$project_root[dev]"
    ;;
  gpu)
    [[ -f "$gpu_lock_file" ]] || { echo "missing GPU dependency lock: $gpu_lock_file" >&2; exit 2; }
    python3 -m pip install --require-hashes -r "$lock_file" -r "$gpu_lock_file"
    python3 -m pip install --no-build-isolation --no-deps --editable "$project_root[dev,gpu]"
    ;;
  *)
    echo "unsupported installer profile: $profile (use full or gpu)" >&2
    exit 2
    ;;
esac

python3 -m pip check
