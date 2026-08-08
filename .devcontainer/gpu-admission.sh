#!/usr/bin/env bash
# @dependency-start
# contract environment
# responsibility Owns the Template explicit GPU-admission lifecycle while
# delegating bootstrap, generation, and finalize to AgentCanon sources.
# upstream design ../vendor/agent-canon/documents/design/devcontainer/parent-devcontainer-policy.md GPU profile boundary
# upstream implementation ../vendor/agent-canon/.devcontainer/gpu-admission.sh accepted host/bootstrap/up/finalize lifecycle
# downstream environment ../docker/packs/gpu-admission.toml explicit GPU image target
# @dependency-end
set -euo pipefail

fail() { printf 'GPU admission opt-in failed: %s\n' "$1" >&2; exit 1; }
[ "$#" -eq 0 ] || fail 'the profile entrypoint does not accept positional overrides'
command -v devcontainer >/dev/null 2>&1 || fail 'devcontainer CLI is unavailable'
command -v nvidia-smi >/dev/null 2>&1 || fail 'nvidia-smi is required for the explicit profile'
nvidia-smi -L >/dev/null 2>&1 || fail 'NVIDIA GPU discovery failed'

repository_root="${AGENT_CANON_ACTIVE_REPOSITORY_ROOT:-}"
if [ -z "$repository_root" ]; then
  repository_root="$(git rev-parse --show-toplevel 2>/dev/null)" || fail 'repository root is unavailable'
fi
repository_root="$(cd "$repository_root" && pwd -P)"
profile_config="$repository_root/.devcontainer/gpu-admission/devcontainer.json"
profile_compose="$repository_root/.agent-canon/gpu-admission-compose.generated.yml"
[ -f "$profile_config" ] || fail "GPU-admission selector is unavailable: $profile_config"

resolver=(python3 tools/agent-canon/agent_tools/agent_canon_source_root.py exec)
bootstrap_output="$(mktemp)"
cleanup_required=0

read_profile_project_name() {
  local project_name=""
  [ -f "$profile_compose" ] || return 1
  project_name="$(awk '/^name: / {print $2; exit}' "$profile_compose")"
  [[ "$project_name" =~ ^[a-z0-9][a-z0-9_-]*-gpu-admission$ ]] || return 1
  printf '%s\n' "$project_name"
}

cleanup_profile() {
  local original_rc="$1" project_name="" cleanup_rc=0
  [ -f "$profile_compose" ] || { printf 'GPU_ADMISSION_CLEANUP=skipped original_rc=%s reason=compose-missing path=%s\n' "$original_rc" "$profile_compose" >&2; return 0; }
  project_name="$(read_profile_project_name)" || { printf 'GPU_ADMISSION_CLEANUP=failed original_rc=%s reason=project-name-invalid path=%s\n' "$original_rc" "$profile_compose" >&2; return 1; }
  docker compose --project-name "$project_name" --file "$profile_compose" down --remove-orphans || cleanup_rc=$?
  [ "$cleanup_rc" -eq 0 ] || { printf 'GPU_ADMISSION_CLEANUP=failed original_rc=%s cleanup_rc=%s project=%s compose=%s\n' "$original_rc" "$cleanup_rc" "$project_name" "$profile_compose" >&2; return "$cleanup_rc"; }
  printf 'GPU_ADMISSION_CLEANUP=pass original_rc=%s project=%s compose=%s\n' "$original_rc" "$project_name" "$profile_compose" >&2
}

on_exit() {
  local original_rc=$? cleanup_rc=0
  trap - EXIT
  set +e
  rm -f "$bootstrap_output"
  if [ "$original_rc" -ne 0 ] && [ "$cleanup_required" -eq 1 ]; then
    cleanup_profile "$original_rc" || cleanup_rc=$?
    [ "$cleanup_rc" -eq 0 ] || printf 'GPU_ADMISSION_CLEANUP_RESULT=failed original_rc=%s cleanup_rc=%s\n' "$original_rc" "$cleanup_rc" >&2
  fi
  exit "$original_rc"
}
trap on_exit EXIT

if ! AGENT_CANON_GPU_ADMISSION_PROFILE=gpu-admission AGENT_CANON_RUNTIME_ROUTE=MANAGED_CONTAINER AGENT_CANON_OPTIONAL_MOUNTS=shared-runtime \
  "${resolver[@]}" .devcontainer/bootstrap-shared-runtime.sh >"$bootstrap_output"; then
  cat "$bootstrap_output" >&2
  exit 1
fi
cat "$bootstrap_output"
read_bootstrap_value() { local key="$1"; awk -F= -v expected_key="$key" '$1 == expected_key {sub(/^[^=]*=/, ""); print; exit}' "$bootstrap_output"; }
runtime_gid="$(read_bootstrap_value AGENT_CANON_RUNTIME_GID)"
host_supplementary_gids="$(read_bootstrap_value AGENT_CANON_HOST_SUPPLEMENTARY_GIDS)"
runtime_source="$(read_bootstrap_value AGENT_CANON_SHARED_RUNTIME_SOURCE)"
provision_receipt="$(read_bootstrap_value AGENT_CANON_SHARED_RUNTIME_PROVISION_RECEIPT)"
[ -n "$runtime_gid" ] || fail 'bootstrap did not return the runtime GID'
[ -n "$host_supplementary_gids" ] || fail 'bootstrap did not return complete host supplementary GIDs'
[ -n "$runtime_source" ] || fail 'bootstrap did not return the runtime source'
[ -n "$provision_receipt" ] || fail 'bootstrap did not return the provision receipt'
expected_host_supplementary_gids="$(id -G | tr ' ' '\n' | sort -n | uniq | tr '\n' ' ' | sed 's/[[:space:]]*$//')"
[ "$host_supplementary_gids" = "$expected_host_supplementary_gids" ] || fail 'bootstrap host supplementary GIDs changed before Compose projection'

export AGENT_CANON_GPU_ADMISSION_PROFILE=gpu-admission AGENT_CANON_RUNTIME_ROUTE=MANAGED_CONTAINER AGENT_CANON_OPTIONAL_MOUNTS=shared-runtime
export AGENT_CANON_RUNTIME_GID="$runtime_gid" AGENT_CANON_HOST_SUPPLEMENTARY_GIDS="$host_supplementary_gids"
export AGENT_CANON_SHARED_RUNTIME_SOURCE="$runtime_source" AGENT_CANON_SHARED_RUNTIME_PROVISION_RECEIPT="$provision_receipt"
export AGENT_CANON_SHARED_RUNTIME_READBACK_RECEIPT="${runtime_source}/shared-runtime-readback.json"
cleanup_required=1
devcontainer up --workspace-folder "$repository_root" --config "$profile_config"
container_repository_root="/workspace/$(basename "$repository_root")"
devcontainer exec --workspace-folder "$repository_root" --config "$profile_config" \
  python3 "$container_repository_root/tools/agent-canon/agent_tools/agent_canon_source_root.py" exec .devcontainer/finalize-shared-runtime.sh
cleanup_required=0
printf 'GPU_ADMISSION_PROFILE=pass selector=%s compose_project_suffix=-gpu-admission runtime=%s target=gpu-runtime\n' "$profile_config" "$runtime_source"
