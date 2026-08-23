#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

if [[ -n "$(git status --short --untracked-files=all)" ]]; then
  echo "fresh-clone acceptance requires a clean committed tree" >&2
  exit 1
fi

mkdir -p "$repo_root/workspace"
workdir="$(mktemp -d "$repo_root/workspace/fresh-clone.XXXXXX")"
cleanup() {
  find "$workdir" -depth -delete 2>/dev/null || true
  rmdir "$repo_root/workspace" 2>/dev/null || true
}
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

find "$template_clone" -depth -delete
git clone "$bare_remote" "$descendant_clone" >/dev/null

(
  cd "$descendant_clone"
  test "$(git branch --show-current)" = main
  if [[ -f .gitmodules ]] && grep -Eiq 'agent[-_[:space:]]*canon' .gitmodules; then
    echo "fresh clone contains AgentCanon submodule metadata" >&2
    exit 1
  fi
  if git ls-files -s | awk '$1 == 160000 { print $4 }' | grep -Eiq 'agent[-_]?canon'; then
    echo "fresh clone contains an AgentCanon gitlink" >&2
    exit 1
  fi
  test ! -e vendor/agent-canon
  test ! -e .agent-canon
  test -x test/testrunner.sh
  test -x scripts/agent-canon-develop.sh
  grep -Fq 'name = "descendant-fixture"' pyproject.toml
  grep -Fq 'project(descendant_fixture VERSION' CMakeLists.txt
  python3 tools/check_runtime_independence.py
  python3 tools/check_markdown_links.py
  python3 tools/check_github_workflows.py
  cmake -S . -B build/fresh-clone -DCMAKE_BUILD_TYPE=Debug
  cmake --build build/fresh-clone --parallel
  ctest --test-dir build/fresh-clone --output-on-failure

  test -z "$(git status --short --untracked-files=all)"
)

printf 'FRESH_CLONE_ACCEPTANCE=pass cmake=pass docker=not-applicable\n'
