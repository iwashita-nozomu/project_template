#!/usr/bin/env bash
set -euo pipefail

gpu_status="disabled"
if [ "${DEVCONTAINER_GPU_MODE:-disabled}" = "enabled" ]; then
  gpu_status="enabled"
fi

mnt_git_status="not-mounted"
if [ -d /mnt/git ]; then
  mnt_git_status="mounted"
fi

docker_socket_status="unavailable"
if [ -S /var/run/docker.sock ]; then
  docker_socket_status="mounted"
fi

echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "project-template devcontainer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "workspace: /workspace"
echo "gpu: ${gpu_status}"
echo "/mnt/git: ${mnt_git_status}"
echo "docker-socket: ${docker_socket_status}"
echo "pythonpath: ${PYTHONPATH:-<unset>}"
echo
echo "quick checks:"
echo "  make ci-quick"
echo "  make docs-check"
echo "  make docker-build-check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
