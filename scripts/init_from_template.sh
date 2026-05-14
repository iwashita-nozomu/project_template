#!/usr/bin/env bash
# @dependency-start
# responsibility Initializes a template-derived repository without mutating shared AgentCanon-owned runtime views.
# upstream design ../vendor/agent-canon/documents/github-first-module-and-devcontainer-policy.md defines shared devcontainer ownership.
# upstream design ../vendor/agent-canon/CONTAINER_OPERATIONS.md defines Docker and devcontainer boundary rules.
# downstream implementation start_repository.sh wraps this initializer.
# downstream implementation ../tests/tools/test_start_repository_script.py verifies dry-run and AgentCanon seeding behavior.
# @dependency-end

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  bash scripts/init_from_template.sh --project-slug <slug> [options]

Options:
  --project-slug <slug>      Required. Kebab-case project slug.
  --display-name <name>      Optional. Human-facing display name.
  --python-package <name>    Optional. Defaults to slug with '-' replaced by '_'.
  --bare-repo <name>.git     Optional. Defaults to <slug>.git.
  --agent-canon-bare-repo <name>.git
                            Optional. Defaults to <slug>-agent-canon.git.
  --skip-agent-canon-bare-repo
                            Do not create or seed the project-local agent-canon bare repo.
  --force                    Allow running with a dirty worktree.
  --dry-run                  Print the planned updates without writing files.
EOF
}

PROJECT_SLUG=""
DISPLAY_NAME=""
PYTHON_PACKAGE=""
BARE_REPO=""
AGENT_CANON_BARE_REPO=""
BARE_GIT_ROOT="${TEMPLATE_BARE_GIT_ROOT:-/mnt/git}"
SKIP_AGENT_CANON_BARE_REPO=0
FORCE=0
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-slug)
      PROJECT_SLUG="${2:-}"
      shift 2
      ;;
    --display-name)
      DISPLAY_NAME="${2:-}"
      shift 2
      ;;
    --python-package)
      PYTHON_PACKAGE="${2:-}"
      shift 2
      ;;
    --bare-repo)
      BARE_REPO="${2:-}"
      shift 2
      ;;
    --agent-canon-bare-repo)
      AGENT_CANON_BARE_REPO="${2:-}"
      shift 2
      ;;
    --skip-agent-canon-bare-repo)
      SKIP_AGENT_CANON_BARE_REPO=1
      shift
      ;;
    --force)
      FORCE=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "${PROJECT_SLUG}" ]]; then
  echo "--project-slug is required" >&2
  usage >&2
  exit 2
fi

if [[ ! "${PROJECT_SLUG}" =~ ^[a-z0-9][a-z0-9._-]*$ ]]; then
  echo "project slug must be lowercase and shell-safe: ${PROJECT_SLUG}" >&2
  exit 2
fi

if [[ -z "${DISPLAY_NAME}" ]]; then
  DISPLAY_NAME="${PROJECT_SLUG}"
fi

if [[ -z "${PYTHON_PACKAGE}" ]]; then
  PYTHON_PACKAGE="${PROJECT_SLUG//-/_}"
fi

if [[ -z "${BARE_REPO}" ]]; then
  BARE_REPO="${PROJECT_SLUG}.git"
fi

if [[ -z "${AGENT_CANON_BARE_REPO}" ]]; then
  AGENT_CANON_BARE_REPO="${PROJECT_SLUG}-agent-canon.git"
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [[ "${DRY_RUN}" != "1" ]] && [[ "${FORCE}" != "1" ]] && [[ -n "$(git status --short)" ]]; then
  echo "worktree is dirty; commit, stash, or rerun with --force" >&2
  exit 1
fi

export TEMPLATE_PROJECT_SLUG="${PROJECT_SLUG}"
export TEMPLATE_DISPLAY_NAME="${DISPLAY_NAME}"
export TEMPLATE_PYTHON_PACKAGE="${PYTHON_PACKAGE}"
export TEMPLATE_BARE_REPO="${BARE_REPO}"
export TEMPLATE_AGENT_CANON_BARE_REPO="${AGENT_CANON_BARE_REPO}"
export TEMPLATE_DRY_RUN="${DRY_RUN}"

python3 - <<'PY'
from __future__ import annotations

import os
from pathlib import Path

root = Path.cwd()
project_slug = os.environ["TEMPLATE_PROJECT_SLUG"]
display_name = os.environ["TEMPLATE_DISPLAY_NAME"]
python_package = os.environ["TEMPLATE_PYTHON_PACKAGE"]
bare_repo = os.environ["TEMPLATE_BARE_REPO"]
agent_canon_bare_repo = os.environ["TEMPLATE_AGENT_CANON_BARE_REPO"]
dry_run = os.environ["TEMPLATE_DRY_RUN"] == "1"

replacements: dict[str, list[tuple[str, str]]] = {
    "pyproject.toml": [
        ('name = "project-template"', f'name = "{project_slug}"'),
    ],
    "README.md": [
        ("# Project Template", f"# {display_name}"),
        ("docker build -t project-template -f docker/Dockerfile .", f"docker build -t {project_slug} -f docker/Dockerfile ."),
        ("  project-template bash", f"  {project_slug} bash"),
        ("/mnt/git/template.git", f"/mnt/git/{bare_repo}"),
    ],
    "QUICK_START.md": [
        ("docker build -t project-template -f docker/Dockerfile .", f"docker build -t {project_slug} -f docker/Dockerfile ."),
        ("  project-template bash", f"  {project_slug} bash"),
        ("/mnt/git/template.git", f"/mnt/git/{bare_repo}"),
    ],
    "docker/packs/default.toml": [
        ('image_tag = "project-template:default-runtime-pack"', f'image_tag = "{project_slug}:default-runtime-pack"'),
    ],
    "docker/packs/default-host-docker.toml": [
        ('image_tag = "project-template:default-runtime-pack-host-docker"', f'image_tag = "{project_slug}:default-runtime-pack-host-docker"'),
    ],
    "documents/templates/server_runtime_layout.template.toml": [
        ('local_state_root = "/var/lib/project-template"', f'local_state_root = "/var/lib/{project_slug}"'),
        ('artifact_root = "/mnt/l/workspace/project_template/reports"', f'artifact_root = "/mnt/l/workspace/{project_slug}/reports"'),
    ],
    "documents/templates/remote_execution_repo.template.toml": [
        ('id = "project-template"', f'id = "{project_slug}"'),
        ('label = "project-template"', f'label = "{display_name}"'),
        ('clone_url = "git@github.com:example/project-template.git"', f'clone_url = "git@github.com:example/{project_slug}.git"'),
    ],
    "documents/linux-wsl-host-requirements.md": [
        ("/mnt/git/template.git", f"/mnt/git/{bare_repo}"),
        ("/mnt/git/agent-canon.git", f"/mnt/git/{agent_canon_bare_repo}"),
    ],
}

for relative_path, pairs in replacements.items():
    path = root / relative_path
    if not path.exists():
        if dry_run:
            print(f"would skip missing {relative_path}")
        continue
    text = path.read_text(encoding="utf-8")
    original = text
    for before, after in pairs:
        text = text.replace(before, after)
    if text == original:
        continue
    if dry_run:
        print(f"would update {relative_path}")
    else:
        path.write_text(text, encoding="utf-8")
        print(f"updated {relative_path}")

print(f"project_slug={project_slug}")
print(f"display_name={display_name}")
print(f"python_package={python_package}")
print(f"bare_repo={bare_repo}")
print(f"agent_canon_bare_repo={agent_canon_bare_repo}")
PY

seed_agent_canon_bare_repo() {
  local bare_repo_path="${BARE_GIT_ROOT}/${AGENT_CANON_BARE_REPO}"
  local proposal_branch="canon-proposal/${PROJECT_SLUG}"
  local canon_dir="${ROOT_DIR}/vendor/agent-canon"
  local canon_toplevel=""
  local tmp_dir=""
  local work_dir=""
  local seed_method=""

  if [[ "${SKIP_AGENT_CANON_BARE_REPO}" == "1" ]]; then
    echo "agent_canon_bare_repo=skipped"
    return
  fi

  if [[ "${DRY_RUN}" == "1" ]]; then
    echo "would seed agent_canon_bare_repo=${bare_repo_path}"
    echo "would prepare agent_canon_proposal_branch=${proposal_branch}"
    return
  fi

  if [[ ! -d "${BARE_GIT_ROOT}" ]]; then
    echo "agent_canon_bare_repo=skipped_missing_${BARE_GIT_ROOT}"
    return
  fi

  if [[ ! -d "${canon_dir}" ]]; then
    echo "agent_canon_bare_repo=skipped_missing_vendor_agent_canon"
    return
  fi

  git init --bare --initial-branch=main "${bare_repo_path}" >/dev/null
  canon_toplevel="$(git -C "${canon_dir}" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ "${canon_toplevel}" == "$(cd "${canon_dir}" && pwd -P)" ]]; then
    git -C "${canon_dir}" push --force "${bare_repo_path}" \
      "HEAD:refs/heads/main" \
      "HEAD:refs/heads/${proposal_branch}" >/dev/null
    seed_method="submodule_head"
  else
    tmp_dir="$(mktemp -d)"
    work_dir="${tmp_dir}/agent-canon-snapshot"
    mkdir -p "${work_dir}"
    (cd "${canon_dir}" && tar --exclude=.git -cf - .) | (cd "${work_dir}" && tar -xf -)
    git -C "${work_dir}" init --initial-branch=main >/dev/null
    git -C "${work_dir}" config user.name "Agent Canon Seeder"
    git -C "${work_dir}" config user.email "agent-canon-seeder@example.invalid"
    git -C "${work_dir}" add -A
    git -C "${work_dir}" commit -m "Seed AgentCanon snapshot" >/dev/null
    git -C "${work_dir}" branch -M main
    git -C "${work_dir}" push --force "${bare_repo_path}" \
      "main:refs/heads/main" \
      "main:refs/heads/${proposal_branch}" >/dev/null
    rm -rf "${tmp_dir}"
    seed_method="snapshot_tree"
  fi

  if git remote get-url agent-canon >/dev/null 2>&1; then
    git remote set-url agent-canon "${bare_repo_path}"
  else
    git remote add agent-canon "${bare_repo_path}"
  fi
  git config agent-canon.proposalBranch "${proposal_branch}"

  echo "agent_canon_bare_repo=${bare_repo_path}"
  echo "agent_canon_seed_method=${seed_method}"
  echo "agent_canon_proposal_branch=${proposal_branch}"
}

ensure_agent_canon_submodule_checkout() {
  local relative_path="vendor/agent-canon"
  local canon_dir="${ROOT_DIR}/${relative_path}"
  local canon_toplevel=""
  local pin=""
  local remote_url=""

  if [[ "$(git ls-tree HEAD "${relative_path}" 2>/dev/null | awk '{print $1}')" != "160000" ]]; then
    return
  fi
  if [[ ! -d "${canon_dir}" ]]; then
    pin="$(git rev-parse "HEAD:${relative_path}")"
    remote_url="$(git config -f .gitmodules --get "submodule.${relative_path}.url")"
    git clone --no-checkout "${remote_url}" "${canon_dir}" >/dev/null
    git -C "${canon_dir}" checkout --detach "${pin}" >/dev/null
    echo "agent_canon_submodule_checkout=initialized"
    return
  fi

  canon_toplevel="$(git -C "${canon_dir}" rev-parse --show-toplevel 2>/dev/null || true)"
  if [[ "${canon_toplevel}" == "$(cd "${canon_dir}" && pwd -P)" ]]; then
    return
  fi

  rm -rf "${canon_dir}"
  pin="$(git rev-parse "HEAD:${relative_path}")"
  remote_url="$(git config -f .gitmodules --get "submodule.${relative_path}.url")"
  git clone --no-checkout "${remote_url}" "${canon_dir}" >/dev/null
  git -C "${canon_dir}" checkout --detach "${pin}" >/dev/null
  echo "agent_canon_submodule_checkout=repaired"
}

seed_agent_canon_bare_repo
if [[ "${DRY_RUN}" != "1" ]]; then
  ensure_agent_canon_submodule_checkout
fi

if [[ "${DRY_RUN}" != "1" ]]; then
  echo "next:"
  echo "  1. Review git diff"
  echo "  2. Push the project branch to ${BARE_GIT_ROOT}/${BARE_REPO} or your chosen origin"
  echo "  3. Run make agent-canon-ensure-latest"
  echo "  4. Run make fresh-clone-check"
fi
