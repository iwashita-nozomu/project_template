#!/usr/bin/env bash
# @dependency-start
# responsibility Runs devcontainer post-create setup after the workspace is mounted.
# upstream environment devcontainer.json postCreateCommand entrypoint
# upstream environment ../docker/install_python_dependencies.sh installs Python dependencies
# upstream environment ../docker/register_safe_directories.sh registers workspace safe directories
# @dependency-end

set -euo pipefail

workspace="${1:-/workspace}"

bash "${workspace%/}/docker/register_safe_directories.sh" "$workspace"
bash "${workspace%/}/docker/install_python_dependencies.sh" "$workspace"
