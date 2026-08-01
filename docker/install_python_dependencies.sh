#!/usr/bin/env bash
# @dependency-start
# contract environment
# responsibility Installs the generated parent Python lock and editable project after the workspace is mounted.
# upstream environment ../pyproject.toml parent direct dependency declarations
# upstream environment requirements.txt generated parent dependency lock
# upstream design ../vendor/agent-canon/CONTAINER_OPERATIONS.md parent Python dependency boundary
# upstream environment ../vendor/agent-canon/.devcontainer/post-create.sh devcontainer post-create entrypoint
# downstream environment ../.github/workflows/ci.yml installs CI Python dependencies through this script
# downstream environment ../.github/workflows/agent-coordination.yml installs dependencies for Python-dependent jobs
# downstream environment packs/default.toml smoke-runs this installer before Python-dependent checks
# @dependency-end

set -euo pipefail

workspace="${1:-/workspace}"
project_root="${workspace%/}"
lock_file="${project_root}/docker/requirements.txt"
project_file="${project_root}/pyproject.toml"

if [ ! -f "$lock_file" ]; then
  printf 'missing generated lock file: %s\n' "$lock_file" >&2
  exit 2
fi
if [ ! -f "$project_file" ]; then
  printf 'missing project metadata: %s\n' "$project_file" >&2
  exit 2
fi

python3 -m pip install --no-cache-dir --require-hashes -r "$lock_file"
python3 -m pip install --no-cache-dir --no-build-isolation --no-deps --editable "${project_root}[dev]"
python3 -m pip check
