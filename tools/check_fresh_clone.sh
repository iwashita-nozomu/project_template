#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
cd "$repo_root"

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
  test -f .gitmodules
  test "$(git config --file .gitmodules --get submodule.vendor/agent-canon.path)" = vendor/agent-canon
  test "$(git ls-files -s vendor/agent-canon | awk '{print $1}')" = 160000
  test ! -e vendor/agent-canon/.git
  if [[ -d vendor/agent-canon ]]; then
    test -z "$(find vendor/agent-canon -mindepth 1 -maxdepth 1 -print -quit)"
  fi
  test ! -e .agent-canon
  make pr-check

  if [[ "${TEMPLATE_FRESH_CLONE_RUN_DOCKER:-0}" == 1 ]]; then
    # CMake caches contain absolute paths and cannot cross the host/container mount boundary.
    make clean-generated
    image="descendant-fixture:fresh-clone"
    docker build --platform linux/amd64 \
      --build-arg "PROJECT_UID=$(id -u)" \
      --build-arg "PROJECT_GID=$(id -g)" \
      --tag "$image" --file docker/Dockerfile .
    docker run --rm --platform linux/amd64 \
      --mount "type=bind,src=$descendant_clone,dst=/workspace/descendant-fixture" \
      --workdir /workspace/descendant-fixture \
      "$image" /bin/bash -lc \
      'bash docker/install_python_dependencies.sh "$PWD" && make pr-check'
  fi

  test -z "$(git status --short --untracked-files=all)"
)

printf 'FRESH_CLONE_ACCEPTANCE=pass docker=%s\n' "${TEMPLATE_FRESH_CLONE_RUN_DOCKER:-0}"
