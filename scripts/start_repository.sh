#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash scripts/start_repository.sh --project-slug <slug> [init options]
  bash scripts/start_repository.sh --validate-only [validation options]

Wrapper options:
  --dry-run                  Run the initializer in preview mode and exit.
  --skip-preflight-dry-run   Skip the default preview before real initialization.
  --validate-only            Run post-commit read-only validation only.
  --skip-fresh-clone-check   With --validate-only, skip descendant clone acceptance.
  -h, --help                 Show this help.
USAGE
}

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
INIT_SCRIPT="$ROOT_DIR/scripts/init_from_template.sh"
DRY_RUN_ONLY=0
PREFLIGHT_DRY_RUN=1
VALIDATE_ONLY=0
RUN_FRESH_CLONE_CHECK=1
INIT_ARGS=()

run_step() {
  printf '==> '
  printf '%q ' "$@"
  printf '\n'
  "$@"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN_ONLY=1; shift ;;
    --skip-preflight-dry-run) PREFLIGHT_DRY_RUN=0; shift ;;
    --validate-only) VALIDATE_ONLY=1; PREFLIGHT_DRY_RUN=0; shift ;;
    --skip-fresh-clone-check) RUN_FRESH_CLONE_CHECK=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) INIT_ARGS+=("$1"); shift ;;
  esac
done

cd "$ROOT_DIR"

if [[ "$VALIDATE_ONLY" == 1 ]]; then
  [[ ${#INIT_ARGS[@]} -eq 0 ]] || { echo "--validate-only does not accept init options" >&2; exit 2; }
  initial_status="$(git status --short --untracked-files=all)"
  [[ -z "$initial_status" ]] || {
    printf '%s\n' "$initial_status"
    echo "--validate-only requires a clean worktree" >&2
    exit 1
  }
  run_step bash "$ROOT_DIR/test/testrunner.sh"
  if [[ "$RUN_FRESH_CLONE_CHECK" == 1 ]]; then
    run_step bash "$ROOT_DIR/tools/check_fresh_clone.sh"
  fi
  final_status="$(git status --short --untracked-files=all)"
  [[ -z "$final_status" ]] || {
    printf '%s\n' "$final_status"
    echo "--validate-only detected worktree drift" >&2
    exit 1
  }
  echo "start_repository_mode=validate_only_readonly"
  echo "start_repository_validation=pass"
  exit 0
fi

if [[ "$DRY_RUN_ONLY" == 1 ]]; then
  run_step bash "$INIT_SCRIPT" "${INIT_ARGS[@]}" --dry-run
  echo "start_repository_mode=dry_run_only"
  exit 0
fi

if [[ "$PREFLIGHT_DRY_RUN" == 1 ]]; then
  run_step bash "$INIT_SCRIPT" "${INIT_ARGS[@]}" --dry-run
fi
run_step bash "$INIT_SCRIPT" "${INIT_ARGS[@]}"
echo "start_repository_init=pass"
echo "next: commit the initialization changes, then run bash scripts/start_repository.sh --validate-only"
