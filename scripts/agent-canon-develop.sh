#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  scripts/agent-canon-develop.sh clone <qualified-task> [branch]
  scripts/agent-canon-develop.sh status <qualified-task>
  scripts/agent-canon-develop.sh refresh <qualified-task>
  scripts/agent-canon-develop.sh cleanup <qualified-task>

The clone is always created below the ignored
workspace/agent-canondevelop/<qualified-task>/agent-canon path. Cleanup requires
a clean checkout whose HEAD is contained in origin/main and releases every
recorded bootstrap runtime below the same qualified task first.
USAGE
}

[[ $# -ge 2 ]] || { usage >&2; exit 2; }
operation="$1"
qualified_task="$2"
branch_name="${3:-}"

[[ "$qualified_task" =~ ^[a-z0-9][a-z0-9._-]*$ ]] || {
  echo "qualified-task must be a lowercase filesystem-safe identifier" >&2
  exit 2
}

project_root="$(git -C "$(dirname "${BASH_SOURCE[0]}")/.." rev-parse --show-toplevel)"
workspace_root="$project_root/workspace"
develop_root="$project_root/workspace/agent-canondevelop"
task_root="$develop_root/$qualified_task"
clone_root="$task_root/agent-canon"
runtime_root="$project_root/workspace/agent-canon-runtime/$qualified_task"
remote_url="${AGENT_CANON_DEVELOP_REMOTE:-https://github.com/iwashita-nozomu/agent-canon.git}"

# The lifecycle helper is allowed to write only below the repository's
# ignored workspace. Do not follow a user-created symlink at any boundary;
# this keeps clone and cleanup operations from escaping into another tree.
for boundary in "$workspace_root" "$develop_root" "$task_root"; do
  [[ ! -L "$boundary" ]] || {
    echo "refusing symlinked development workspace boundary: $boundary" >&2
    exit 1
  }
done

require_clone() {
  git -C "$clone_root" rev-parse --show-toplevel >/dev/null 2>&1 || {
    echo "AgentCanon development clone is missing: $clone_root" >&2
    exit 1
  }
}

case "$operation" in
  clone)
    [[ ! -e "$task_root" ]] || {
      echo "qualified task already exists: $task_root" >&2
      exit 1
    }
    mkdir -p "$task_root"
    clone_args=(clone --origin origin "$remote_url" "$clone_root")
    if [[ -n "$branch_name" ]]; then
      clone_args=(clone --origin origin --branch "$branch_name" "$remote_url" "$clone_root")
    fi
    if ! git "${clone_args[@]}"; then
      find "$task_root" -depth -delete 2>/dev/null || true
      exit 1
    fi
    printf 'AGENT_CANON_DEVELOP_CLONE=%s\n' "$clone_root"
    ;;
  status)
    require_clone
    git -C "$clone_root" status --short --branch
    git -C "$clone_root" remote -v
    if [[ -d "$runtime_root" ]]; then
      printf 'runtime=%s\n' "$runtime_root"
    fi
    ;;
  refresh)
    require_clone
    git -C "$clone_root" fetch --prune origin
    git -C "$clone_root" status --short --branch
    ;;
  cleanup)
    require_clone
    [[ -z "$(git -C "$clone_root" status --short --untracked-files=all)" ]] || {
      echo "cleanup refused: AgentCanon checkout is dirty" >&2
      exit 1
    }
    git -C "$clone_root" fetch --prune origin main
    git -C "$clone_root" merge-base --is-ancestor HEAD origin/main || {
      echo "cleanup refused: checkout HEAD is not contained in origin/main" >&2
      exit 1
    }
    if [[ -d "$runtime_root" ]]; then
      "$clone_root/bootstrap.sh" \
        --control-parent-root "$project_root" \
        --runtime-root "$runtime_root" uninstall
      find "$runtime_root" -depth -delete
    fi
    find "$task_root" -depth -delete
    rmdir "$develop_root" "$project_root/workspace/agent-canon-runtime" \
      "$workspace_root" 2>/dev/null || true
    printf 'AGENT_CANON_DEVELOP_CLEANUP=%s\n' "$qualified_task"
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
