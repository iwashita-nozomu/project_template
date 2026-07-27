#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
parent_root="$(cd "$script_dir/.." && pwd -P)"

"$parent_root/vendor/agent-canon/.devcontainer/bootstrap-shared-runtime.sh"
