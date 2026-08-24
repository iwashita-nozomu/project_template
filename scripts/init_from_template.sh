#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  bash scripts/init_from_template.sh --project-slug <slug> [options]

Options:
  --project-slug <slug>      Required. Kebab-case project slug.
  --display-name <name>      Optional. Human-facing display name.
  --force                    Allow running with a dirty worktree.
  --dry-run                  Print the planned updates without writing files.
USAGE
}

PROJECT_SLUG=""
DISPLAY_NAME=""
FORCE=0
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-slug) PROJECT_SLUG="${2:-}"; shift 2 ;;
    --display-name) DISPLAY_NAME="${2:-}"; shift 2 ;;
    --force) FORCE=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ -n "$PROJECT_SLUG" ]] || { echo "--project-slug is required" >&2; usage >&2; exit 2; }
[[ "$PROJECT_SLUG" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || {
  echo "project slug must be lowercase kebab-case: $PROJECT_SLUG" >&2
  exit 2
}
DISPLAY_NAME="${DISPLAY_NAME:-$PROJECT_SLUG}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$ROOT_DIR"

if [[ "$DRY_RUN" != 1 && "$FORCE" != 1 && -n "$(git status --short --untracked-files=all)" ]]; then
  echo "worktree is dirty; commit, stash, or rerun with --force" >&2
  exit 1
fi

export TEMPLATE_PROJECT_SLUG="$PROJECT_SLUG"
export TEMPLATE_DISPLAY_NAME="$DISPLAY_NAME"
export TEMPLATE_DRY_RUN="$DRY_RUN"

python3 - <<'PY'
from __future__ import annotations

import os
from pathlib import Path

root = Path.cwd()
slug = os.environ["TEMPLATE_PROJECT_SLUG"]
display = os.environ["TEMPLATE_DISPLAY_NAME"]
cmake_name = slug.replace("-", "_")
dry_run = os.environ["TEMPLATE_DRY_RUN"] == "1"

replacements: dict[str, list[tuple[str, str]]] = {
    "pyproject.toml": [('name = "project-template"', f'name = "{slug}"')],
    "README.md": [
        ("# Project Template", f"# {display}"),
        ("bash docker/run-tests.sh --tag project-template:test", f"bash docker/run-tests.sh --tag {slug}:test"),
    ],
    "QUICK_START.md": [
        ("bash docker/run-tests.sh --tag project-template:test", f"bash docker/run-tests.sh --tag {slug}:test"),
    ],
    "CMakeLists.txt": [
        ("project(project_template VERSION", f"project({cmake_name} VERSION"),
    ],
    "docker/README.md": [
        ("project-template:test", f"{slug}:test"),
    ],
    "docker/run-tests.sh": [
        ("image_tag=project-template:test", f"image_tag={slug}:test"),
    ],
    "documents/contracts/linux-wsl-host-requirements.md": [
        ("project-template:host-check", f"{slug}:host-check"),
    ],
    "documents/contracts/template-bootstrap.md": [
        ("`project-template`", f"`{slug}`"),
    ],
}

changed: list[str] = []
for relative, pairs in replacements.items():
    path = root / relative
    text = path.read_text(encoding="utf-8")
    updated = text
    for before, after in pairs:
        updated = updated.replace(before, after)
    if updated == text:
        continue
    changed.append(relative)
    if dry_run:
        print(f"would update {relative}")
    else:
        path.write_text(updated, encoding="utf-8")
        print(f"updated {relative}")

print(f"project_slug={slug}")
print(f"display_name={display}")
print(f"cmake_project={cmake_name}")
print("template_bootstrap=local_offline")
print("project_runtime=source_free")
print(f"changed_files={len(changed)}")
PY

if [[ "$DRY_RUN" != 1 ]]; then
  echo "next: review the diff, commit it, run bash test/testrunner.sh, then run bash tools/check_fresh_clone.sh"
fi
