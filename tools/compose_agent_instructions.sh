#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  printf 'usage: %s /path/to/agent-canon\n' "$0" >&2
  exit 2
fi

agent_canon_root=$1
script_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
composer="$agent_canon_root/tools/agent_tools/entrypoint_composer.py"
base="$agent_canon_root/ROOT_AGENTS.md"
specific="$script_root/documents/agent-canon/consumer-root-instructions.md"
output="$script_root/AGENTS.md"

if [[ ! -d "$agent_canon_root" || ! -f "$composer" || ! -f "$base" ]]; then
  printf 'AgentCanon source checkout is missing ROOT_AGENTS.md or the public composer: %s\n' "$agent_canon_root" >&2
  exit 2
fi

exec python3 "$composer" \
  --base "$base" \
  --specific "$specific" \
  --output "$output" \
  --source-root "$agent_canon_root"
