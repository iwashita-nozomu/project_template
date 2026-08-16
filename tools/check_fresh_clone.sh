#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

[[ "${PROJECT_TEMPLATE_IMAGE:-}" == 1 ]] || {
  echo "fresh-clone acceptance must run in the canonical cpu-dev image" >&2
  exit 2
}
[[ -x /opt/project-venv/bin/python ]] || {
  echo "image-owned Python environment is missing" >&2
  exit 2
}
if [[ -n "$(git status --short --untracked-files=all)" ]]; then
  echo "fresh-clone acceptance requires a clean committed tree" >&2
  exit 1
fi

workdir="$(mktemp -d)"
cleanup() { rm -rf "$workdir"; }
trap cleanup EXIT HUP INT TERM

template_clone="$workdir/template"
bare_remote="$workdir/descendant.git"
descendant_clone="$workdir/descendant"

git clone --no-local "$repo_root" "$template_clone" >/dev/null
git -C "$template_clone" config user.email "fixture@localhost"
git -C "$template_clone" config user.name "Fixture"

(
  cd "$template_clone"
  env -u GITHUB_TOKEN -u GH_TOKEN -u SSH_AUTH_SOCK \
    bash scripts/start_repository.sh \
      --project-slug descendant-fixture \
      --display-name "Descendant Fixture" \
      --skip-preflight-dry-run
  git add --all
  git commit -m "Initialize descendant fixture" >/dev/null
  git init --bare "$bare_remote" >/dev/null
  git --git-dir="$bare_remote" config receive.shallowUpdate true
  git remote add fixture "$bare_remote"
  git push fixture HEAD:refs/heads/main >/dev/null
  git --git-dir="$bare_remote" symbolic-ref HEAD refs/heads/main
)

rm -rf "$template_clone"
git clone "$bare_remote" "$descendant_clone" >/dev/null

(
  cd "$descendant_clone"
  test "$(git branch --show-current)" = main
  test ! -e .gitmodules
  test ! -e vendor
  test ! -e .agent-canon
  test ! -e docker/install_python_dependencies.sh
  test ! -e .devcontainer/post-create-parent.sh
  make validation-core-local
  test -z "$(git status --short --untracked-files=all)"
)

printf 'FRESH_CLONE_ACCEPTANCE=pass image=cpu-dev\n'
