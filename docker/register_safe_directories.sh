#!/usr/bin/env bash
# @dependency-start
# responsibility Registers Git safe.directory entries for mounted repo workspaces.
# upstream design ../vendor/agent-canon/CONTAINER_OPERATIONS.md defines dynamic safe.directory policy.
# downstream implementation Dockerfile installs this helper in the project image.
# downstream implementation ../vendor/agent-canon/.devcontainer/post-create.sh calls this helper after mount.
# @dependency-end

set -euo pipefail

workspace="${1:-/workspace}"

register_safe_directory() {
  local path="$1"
  [ -d "$path" ] || return 0
  git config --global --add safe.directory "$path" || true
}

register_safe_directory "$workspace"
register_safe_directory "${workspace%/}/.git"

if [ -d "${workspace%/}/vendor" ]; then
  while IFS= read -r vendor_path; do
    register_safe_directory "$vendor_path"
  done < <(find "${workspace%/}/vendor" -mindepth 1 -maxdepth 1 -type d | sort)
fi
