#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PREFIX="${AGENT_CANON_PREFIX:-vendor/agent-canon}"
REMOTE_NAME="${AGENT_CANON_REMOTE_NAME:-agent-canon}"
DEFAULT_BRANCH="${AGENT_CANON_BRANCH:-main}"

usage() {
  cat <<EOF
Usage:
  bash scripts/sync_agent_canon.sh add <remote-url> [branch]
  bash scripts/sync_agent_canon.sh pull [branch]
  bash scripts/sync_agent_canon.sh push [branch]
  bash scripts/sync_agent_canon.sh status

Environment overrides:
  AGENT_CANON_PREFIX
  AGENT_CANON_REMOTE_NAME
  AGENT_CANON_BRANCH
EOF
}

die() {
  echo "sync_agent_canon.sh: $*" >&2
  exit 1
}

require_git_repo() {
  git -C "$ROOT_DIR" rev-parse --show-toplevel >/dev/null 2>&1 || die "repository root not found"
}

require_clean_worktree() {
  if [ -n "$(git -C "$ROOT_DIR" status --short)" ]; then
    die "worktree is dirty; commit or stash changes before subtree operations"
  fi
}

ensure_remote() {
  local remote_url="$1"
  if git -C "$ROOT_DIR" remote get-url "$REMOTE_NAME" >/dev/null 2>&1; then
    return
  fi
  git -C "$ROOT_DIR" remote add "$REMOTE_NAME" "$remote_url"
}

require_existing_remote() {
  git -C "$ROOT_DIR" remote get-url "$REMOTE_NAME" >/dev/null 2>&1 || die "remote '$REMOTE_NAME' is not configured"
}

cmd_add() {
  local remote_url="$1"
  local branch="${2:-$DEFAULT_BRANCH}"
  require_clean_worktree
  ensure_remote "$remote_url"
  git -C "$ROOT_DIR" fetch "$REMOTE_NAME" "$branch"
  git -C "$ROOT_DIR" subtree add --prefix="$PREFIX" "$REMOTE_NAME" "$branch" --squash
}

cmd_pull() {
  local branch="${1:-$DEFAULT_BRANCH}"
  require_clean_worktree
  require_existing_remote
  git -C "$ROOT_DIR" fetch "$REMOTE_NAME" "$branch"
  git -C "$ROOT_DIR" subtree pull --prefix="$PREFIX" "$REMOTE_NAME" "$branch" --squash
}

cmd_push() {
  local branch="${1:-$DEFAULT_BRANCH}"
  require_clean_worktree
  require_existing_remote
  [ -d "$ROOT_DIR/$PREFIX" ] || die "prefix '$PREFIX' does not exist"
  git -C "$ROOT_DIR" subtree push --prefix="$PREFIX" "$REMOTE_NAME" "$branch"
}

cmd_status() {
  local remote_url=""
  if git -C "$ROOT_DIR" remote get-url "$REMOTE_NAME" >/dev/null 2>&1; then
    remote_url="$(git -C "$ROOT_DIR" remote get-url "$REMOTE_NAME")"
  fi
  echo "repo_root=$ROOT_DIR"
  echo "prefix=$PREFIX"
  echo "remote_name=$REMOTE_NAME"
  echo "default_branch=$DEFAULT_BRANCH"
  if [ -n "$remote_url" ]; then
    echo "remote_url=$remote_url"
  else
    echo "remote_url=<unset>"
  fi
  if [ -d "$ROOT_DIR/$PREFIX" ]; then
    echo "prefix_status=present"
  else
    echo "prefix_status=missing"
  fi
}

main() {
  require_git_repo
  cd "$ROOT_DIR"

  local subcommand="${1:-}"
  case "$subcommand" in
    add)
      [ "${2:-}" ] || die "add requires <remote-url>"
      cmd_add "$2" "${3:-$DEFAULT_BRANCH}"
      ;;
    pull)
      cmd_pull "${2:-$DEFAULT_BRANCH}"
      ;;
    push)
      cmd_push "${2:-$DEFAULT_BRANCH}"
      ;;
    status)
      cmd_status
      ;;
    -h|--help|help|"")
      usage
      ;;
    *)
      die "unknown subcommand '$subcommand'"
      ;;
  esac
}

main "$@"
