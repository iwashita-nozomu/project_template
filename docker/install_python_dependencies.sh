#!/usr/bin/env bash
# @dependency-start
# contract environment
# responsibility Installs full or validation-profile dependencies from the generated parent Python lock.
# upstream environment ../pyproject.toml parent direct dependency declarations
# upstream environment requirements.txt generated parent dependency lock
# upstream design ../vendor/agent-canon/CONTAINER_OPERATIONS.md parent Python dependency boundary
# upstream environment ../vendor/agent-canon/.devcontainer/post-create.sh devcontainer post-create entrypoint
# downstream environment ../.github/workflows/ci.yml installs CI Python dependencies through this script
# downstream environment ../.github/workflows/agent-coordination.yml uses validation for role scope and full for pre-review
# downstream environment packs/default.toml smoke-runs this installer before Python-dependent checks
# @dependency-end

set -euo pipefail

workspace="/workspace"
workspace_set=0
profile="full"

while [ "$#" -gt 0 ]; do
  case "$1" in
    --profile)
      if [ "$#" -lt 2 ]; then
        printf 'missing value for --profile\n' >&2
        exit 2
      fi
      profile="$2"
      shift 2
      ;;
    --profile=*)
      profile="${1#*=}"
      shift
      ;;
    -*)
      printf 'unknown installer option: %s\n' "$1" >&2
      exit 2
      ;;
    *)
      if [ "$workspace_set" -eq 1 ]; then
        printf 'unexpected installer argument: %s\n' "$1" >&2
        exit 2
      fi
      workspace="$1"
      workspace_set=1
      shift
      ;;
  esac
done

project_root="${workspace%/}"
lock_file="${project_root}/docker/requirements.txt"
gpu_lock_file="${project_root}/docker/requirements-gpu.txt"
project_file="${project_root}/pyproject.toml"

if [ ! -f "$lock_file" ]; then
  printf 'missing generated lock file: %s\n' "$lock_file" >&2
  exit 2
fi

extract_locked_requirement() {
  local source_lock="$1"
  local normalized_target="$2"

  LC_ALL=C awk -v target="$normalized_target" '
    function normalize(name) {
      gsub(/[-_.]+/, "-", name)
      return tolower(name)
    }

    function requirement_name(line, name) {
      if (!match(line, /^[[:alnum:]][[:alnum:]._-]*(\[[^][]+\])?==/)) {
        return ""
      }
      name = substr(line, RSTART, RLENGTH)
      sub(/\[.*$/, "", name)
      sub(/==$/, "", name)
      return normalize(name)
    }

    {
      name = requirement_name($0)
      if (name != "") {
        capture = (name == target)
        if (capture) {
          matches++
        }
      }
      if (capture) {
        print
        if (index($0, "--hash=sha256:") > 0) {
          hashes++
        }
      }
    }

    END {
      if (matches != 1 || hashes < 1) {
        printf "locked requirement extraction failed: target=%s matches=%d hashes=%d\n", target, matches, hashes > "/dev/stderr"
        exit 3
      }
    }
  ' "$source_lock"
}

case "$profile" in
  full)
    if [ ! -f "$project_file" ]; then
      printf 'missing project metadata: %s\n' "$project_file" >&2
      exit 2
    fi
    python3 -m pip install --require-hashes -r "$lock_file"
    python3 -m pip install --no-build-isolation --no-deps --editable "${project_root}[dev]"
    python3 -m pip check
    ;;
  gpu)
    if [ ! -f "$project_file" ]; then
      printf 'missing project metadata: %s\n' "$project_file" >&2
      exit 2
    fi
    if [ ! -f "$gpu_lock_file" ]; then
      printf 'missing GPU dependency lock file: %s\n' "$gpu_lock_file" >&2
      exit 2
    fi
    python3 -m pip install --require-hashes -r "$lock_file" -r "$gpu_lock_file"
    python3 -m pip install --no-build-isolation --no-deps --editable "${project_root}[dev,gpu]"
    python3 -m pip check
    ;;
  validation)
    validation_requirements="$(mktemp)"
    trap 'rm -f -- "$validation_requirements"' EXIT
    if ! extract_locked_requirement "$lock_file" pyyaml > "$validation_requirements"; then
      printf 'failed to extract validation dependency from generated lock: %s\n' "$lock_file" >&2
      exit 2
    fi
    python3 -m pip install --require-hashes --no-deps -r "$validation_requirements"
    ;;
  *)
    printf 'unsupported installer profile: %s (use full, gpu, or validation)\n' "$profile" >&2
    exit 2
    ;;
esac
