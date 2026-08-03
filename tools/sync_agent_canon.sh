#!/usr/bin/env bash
# @dependency-start
# contract tool
# responsibility Provides the parent-root adapter to the canonical AgentCanon sync route.
# upstream design ../vendor/agent-canon/documents/runtime/SHARED_RUNTIME_SURFACES.md root-view ownership
# upstream implementation ../vendor/agent-canon/tools/sync_agent_canon.sh canonical sync implementation
# downstream implementation ../AGENTS.md parent runtime entrypoint and update route
# @dependency-end
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"
exec env PYTHONPATH="vendor/agent-canon/tools:tools${PYTHONPATH:+:$PYTHONPATH}" \
  python3 -m agent_tools.agent_canon_source_root exec \
  tools/sync_agent_canon.sh "$@"
