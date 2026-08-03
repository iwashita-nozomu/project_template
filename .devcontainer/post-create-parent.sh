#!/usr/bin/env bash
# @dependency-start
# contract environment
# responsibility 親固有のpost-create final hookをshared AgentCanon stage後にnon-root project userで実行する。
# upstream design ../documents/design/docker-zero-build-environment.md 親runtime順序とfinal hook owner
# upstream design ../vendor/agent-canon/documents/design/devcontainer/parent-devcontainer-policy.md shared post-createと親hook境界
# upstream implementation ../vendor/agent-canon/.devcontainer/post-create.sh shared bootstrapと依存導入
# downstream implementation ../.devcontainer/devcontainer.json shared post-create後にこのhookを呼び出す
# downstream implementation ../docker/Dockerfile shell startupから独立したimage/runtime contract
# @dependency-end

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
