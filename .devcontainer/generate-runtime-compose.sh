#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_FILE="${SCRIPT_DIR}/docker-compose.generated.yml"

has_gpu=0
has_mnt_git=0

if [ -e /dev/nvidiactl ] || command -v nvidia-smi >/dev/null 2>&1; then
  has_gpu=1
fi

if [ -d /mnt/git ]; then
  has_mnt_git=1
fi

cat >"$RUNTIME_FILE" <<'EOF'
services:
  workspace:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    working_dir: /workspace
    volumes:
      - ..:/workspace:cached
EOF

if [ "$has_mnt_git" -eq 1 ]; then
  cat >>"$RUNTIME_FILE" <<'EOF'
      - /mnt/git:/mnt/git
EOF
fi

cat >>"$RUNTIME_FILE" <<'EOF'
    command: /bin/bash -lc "sleep infinity"
    tty: true
    init: true
EOF

if [ "$has_gpu" -eq 1 ]; then
  cat >>"$RUNTIME_FILE" <<'EOF'
    gpus: all
    environment:
      DEVCONTAINER_RUNTIME_MODE: "generated"
      DEVCONTAINER_GPU_MODE: "enabled"
      NVIDIA_VISIBLE_DEVICES: all
      NVIDIA_DRIVER_CAPABILITIES: compute,utility
EOF
else
  cat >>"$RUNTIME_FILE" <<'EOF'
    environment:
      DEVCONTAINER_RUNTIME_MODE: "generated"
      DEVCONTAINER_GPU_MODE: "disabled"
EOF
fi

echo "devcontainer runtime generated: gpu=${has_gpu} mount_mnt_git=${has_mnt_git}"
