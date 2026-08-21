#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(cd "$script_dir/.." && pwd -P)"
workspace="${1:-}"

[[ -n "$workspace" ]] || { echo "post-create validation requires the repository root" >&2; exit 1; }
test "$(id -un)" = project || { echo "expected project user" >&2; exit 1; }
test "$(id -u)" -ne 0 || { echo "must not run as root" >&2; exit 1; }
test "${HOME:-}" = /home/project || { echo "HOME must be /home/project" >&2; exit 1; }
test -z "${ZDOTDIR:-}" || { echo "ZDOTDIR is not accepted" >&2; exit 1; }
sudo -n true
test -w "$workspace" || { echo "workspace is not writable" >&2; exit 1; }
test -f "$HOME/.zshrc" || { echo "image-owned zshrc is missing" >&2; exit 1; }
zsh -fc 'exit 0'

printf 'POST_CREATE_VALIDATION=pass workspace=%s repo_root=%s\n' "$workspace" "$repo_root"
