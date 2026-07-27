#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
parent_root="$(cd "$script_dir/.." && pwd -P)"

workspace="${1:-}"
[ -n "$workspace" ] || {
  echo "post-create requires the selected repository root argument" >&2
  exit 1
}

"$parent_root/vendor/agent-canon/.devcontainer/post-create.sh" "$workspace"
"$script_dir/post-create-parent.sh" "$workspace"
