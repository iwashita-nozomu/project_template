#!/usr/bin/env bash
# @dependency-start
# responsibility Wraps template repository initialization and post-init validation.
# upstream implementation init_from_template.sh performs repository-local slug and AgentCanon seeding.
# upstream implementation ../tools/sync_agent_canon.sh checks AgentCanon freshness.
# downstream implementation ../tests/tools/test_start_repository_script.py validates wrapper behavior.
# @dependency-end

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash scripts/start_repository.sh --project-slug <slug> [init options]
  bash scripts/start_repository.sh --validate-only [validation options]

Init options are passed through to scripts/init_from_template.sh.

Wrapper options:
  --dry-run                  Run init_from_template.sh --dry-run and exit.
  --skip-preflight-dry-run   Skip the default dry-run before real init.
  --skip-agent-canon-check   Skip make agent-canon-ensure-latest.
  --validate-only            Run post-commit validation only.
  --skip-fresh-clone-check   In --validate-only mode, skip make fresh-clone-check.
  --skip-ci-quick            In --validate-only mode, skip make ci-quick.
  -h, --help                 Show this help.

Default init flow:
  1. scripts/init_from_template.sh --dry-run ...
  2. scripts/init_from_template.sh ...
  3. make agent-canon-ensure-latest

Post-commit validation:
  bash scripts/start_repository.sh --validate-only
EOF
}

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INIT_SCRIPT="${ROOT_DIR}/scripts/init_from_template.sh"

DRY_RUN_ONLY=0
PREFLIGHT_DRY_RUN=1
RUN_AGENT_CANON_CHECK=1
VALIDATE_ONLY=0
RUN_FRESH_CLONE_CHECK=1
RUN_CI_QUICK=1
INIT_ARGS=()

run_step() {
  echo "==> $*"
  "$@"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN_ONLY=1
      shift
      ;;
    --skip-preflight-dry-run)
      PREFLIGHT_DRY_RUN=0
      shift
      ;;
    --skip-agent-canon-check)
      RUN_AGENT_CANON_CHECK=0
      shift
      ;;
    --validate-only)
      VALIDATE_ONLY=1
      PREFLIGHT_DRY_RUN=0
      shift
      ;;
    --skip-fresh-clone-check)
      RUN_FRESH_CLONE_CHECK=0
      shift
      ;;
    --skip-ci-quick)
      RUN_CI_QUICK=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      INIT_ARGS+=("$1")
      shift
      ;;
  esac
done

cd "${ROOT_DIR}"

if [[ "${VALIDATE_ONLY}" == "1" ]]; then
  if [[ -n "${INIT_ARGS[*]:-}" ]]; then
    echo "--validate-only does not accept init_from_template.sh options" >&2
    exit 2
  fi
  if [[ -n "$(git status --short)" ]]; then
    echo "--validate-only requires a clean worktree so fresh clone checks read the committed state" >&2
    exit 1
  fi
  if [[ "${RUN_AGENT_CANON_CHECK}" == "1" ]]; then
    run_step make agent-canon-ensure-latest
  fi
  if [[ "${RUN_FRESH_CLONE_CHECK}" == "1" ]]; then
    run_step make fresh-clone-check
  fi
  if [[ "${RUN_CI_QUICK}" == "1" ]]; then
    run_step make ci-quick
  fi
  echo "start_repository_validation=pass"
  exit 0
fi

if [[ "${DRY_RUN_ONLY}" == "1" ]]; then
  run_step bash "${INIT_SCRIPT}" "${INIT_ARGS[@]}" --dry-run
  echo "start_repository_mode=dry_run_only"
  exit 0
fi

if [[ "${PREFLIGHT_DRY_RUN}" == "1" ]]; then
  run_step bash "${INIT_SCRIPT}" "${INIT_ARGS[@]}" --dry-run
fi

run_step bash "${INIT_SCRIPT}" "${INIT_ARGS[@]}"

if [[ "${RUN_AGENT_CANON_CHECK}" == "1" ]]; then
  run_step make agent-canon-ensure-latest
fi

echo "start_repository_init=pass"
echo "next: commit the init changes, then run: bash scripts/start_repository.sh --validate-only"
