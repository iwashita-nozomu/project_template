#!/usr/bin/env bash
# @dependency-start
# contract environment
# responsibility Installs the generated parent Python lock and editable project after the workspace is mounted.
# upstream environment ../pyproject.toml parent direct dependency declarations
# upstream environment requirements.txt generated parent dependency lock
# upstream design ../vendor/agent-canon/CONTAINER_OPERATIONS.md parent Python dependency boundary
# upstream environment ../vendor/agent-canon/.devcontainer/post-create.sh devcontainer post-create entrypoint
# downstream environment ../.github/workflows/ci.yml installs CI Python dependencies through this script
# downstream environment ../.github/workflows/agent-coordination.yml keeps static verifier jobs dependency-free
# downstream environment packs/default.toml smoke-runs this installer before Python-dependent checks
# @dependency-end

set -euo pipefail

workspace="${1:-/workspace}"
project_root="${workspace%/}"
lock_file="${project_root}/docker/requirements.txt"
project_file="${project_root}/pyproject.toml"
marker_dir="${PYTHON_DEPENDENCY_MARKER_DIR:-/usr/local/share/project-template}"
marker="${marker_dir%/}/python-dependencies.sha256"

if [ ! -f "$lock_file" ]; then
  printf 'missing generated lock file: %s\n' "$lock_file" >&2
  exit 2
fi
if [ ! -f "$project_file" ]; then
  printf 'missing project metadata: %s\n' "$project_file" >&2
  exit 2
fi

lock_hash="$(sha256sum "$lock_file" | awk '{print $1}')"
project_hash="$(sha256sum "$project_file" | awk '{print $1}')"
marker_contents="lock=${lock_hash}
project=${project_hash}"

if [ -f "$marker" ] && [ "$(cat "$marker")" = "$marker_contents" ]; then
  if python3 -m pip show project-template >/dev/null 2>&1 \
    && python3 -m pip check >/dev/null; then
    printf 'python_dependencies=up-to-date lock_hash=%s project_hash=%s\n' "$lock_hash" "$project_hash"
    exit 0
  fi
fi

python3 -m pip install --no-cache-dir --require-hashes -r "$lock_file"
python3 -m pip install --no-cache-dir --no-build-isolation --no-deps --editable "${project_root}[dev]"
python3 -m pip check

mkdir -p "$marker_dir"
printf '%s\n' "$marker_contents" > "$marker"
printf 'python_dependencies=installed lock_hash=%s project_hash=%s\n' "$lock_hash" "$project_hash"
