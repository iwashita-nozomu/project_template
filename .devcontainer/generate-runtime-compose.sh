#!/usr/bin/env bash
# @dependency-start
# responsibility Renders devcontainer compose without requiring AgentCanon submodule tooling.
# upstream environment ../docker/packs/default.toml default devcontainer runtime pack
# upstream environment ../docker/README.md devcontainer runtime guidance
# downstream environment devcontainer.json initializeCommand entrypoint
# @dependency-end

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
pack="${repo_root}/docker/packs/default.toml"
output="${repo_root}/.devcontainer/docker-compose.generated.yml"

mapfile -t pack_values < <(
  python3 - "$pack" <<'PY'
from __future__ import annotations

import sys
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[no-redef]

with open(sys.argv[1], "rb") as handle:
    data = tomllib.load(handle)
pack = data["pack"]
runtime = data.get("runtime", {})
print(pack["dockerfile"])
print(runtime.get("workdir", "/workspace"))
print(runtime.get("workspace_mount", "/workspace"))
PY
)

dockerfile="${pack_values[0]}"
workdir="${pack_values[1]}"
workspace_mount="${pack_values[2]}"

volume_lines=("      - ..:${workspace_mount}:cached")
if [ -d /mnt/git ]; then
  volume_lines+=("      - /mnt/git:/mnt/git")
fi
if [ -d "${HOME}/.codex" ]; then
  volume_lines+=("      - ${HOME}/.codex:/root/.codex")
fi
if [ -d "${HOME}/.config/gh" ]; then
  volume_lines+=("      - ${HOME}/.config/gh:/root/.config/gh")
fi
if [ -d "${HOME}/.ssh" ]; then
  volume_lines+=("      - ${HOME}/.ssh:/root/.ssh:ro")
fi
if [ -n "${SSH_AUTH_SOCK:-}" ] && [ -S "${SSH_AUTH_SOCK}" ]; then
  volume_lines+=("      - ${SSH_AUTH_SOCK}:/ssh-agent")
fi

gpu_mode="disabled"
if [ -e /dev/nvidiactl ] || command -v nvidia-smi >/dev/null 2>&1; then
  gpu_mode="enabled"
fi

environment_lines=(
  '      DEVCONTAINER_RUNTIME_MODE: "generated"'
  "      DEVCONTAINER_GPU_MODE: \"${gpu_mode}\""
)
if [ -n "${SSH_AUTH_SOCK:-}" ] && [ -S "${SSH_AUTH_SOCK}" ]; then
  environment_lines+=('      SSH_AUTH_SOCK: "/ssh-agent"')
fi
if [ "$gpu_mode" = "enabled" ]; then
  environment_lines+=(
    "      NVIDIA_VISIBLE_DEVICES: all"
    '      NVIDIA_DRIVER_CAPABILITIES: "compute,utility"'
  )
fi

{
  printf 'services:\n'
  printf '  workspace:\n'
  printf '    build:\n'
  printf '      context: ..\n'
  printf '      dockerfile: %s\n' "$dockerfile"
  printf '    working_dir: %s\n' "$workdir"
  printf '    volumes:\n'
  printf '%s\n' "${volume_lines[@]}"
  printf '    command: /bin/bash -lc "sleep infinity"\n'
  printf '    tty: true\n'
  printf '    init: true\n'
  if [ "$gpu_mode" = "enabled" ]; then
    printf '    gpus: all\n'
  fi
  printf '    environment:\n'
  printf '%s\n' "${environment_lines[@]}"
} > "$output"

printf 'devcontainer runtime generated: gpu=%s pack=docker/packs/default.toml\n' "$gpu_mode"
