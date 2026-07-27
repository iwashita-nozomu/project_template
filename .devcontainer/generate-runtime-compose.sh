#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
parent_root="$(cd "$script_dir/.." && pwd -P)"

export AGENT_CANON_DOCKER_COMPOSE_OUTPUT="$parent_root/.devcontainer/docker-compose.generated.yml"
"$parent_root/vendor/agent-canon/.devcontainer/generate-runtime-compose.sh"
