#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
parent_root="$(cd "$script_dir/.." && pwd -P)"

workspace="${1:-}"
[ -n "$workspace" ] || {
  echo "post-create-parent requires the selected repository root argument" >&2
  exit 1
}

echo "post-create-parent: pass"
echo "workspace: $workspace"
echo "repo-root: $parent_root"
