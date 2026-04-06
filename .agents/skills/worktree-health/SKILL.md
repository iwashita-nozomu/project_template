---
name: worktree-health
description: Use this skill to review current worktree scope, drift, and cleanup readiness.
---

# Worktree Health

1. Read `agents/skills/worktree-health.md`.
1. Open `WORKTREE_SCOPE.md` and the current worktree action log before reviewing git state.
1. Check `git status --short --branch`, `git diff --name-only`, and `git worktree list --porcelain`.
1. Run `bash scripts/tools/check_worktree_scopes.sh` when drift or stale worktrees are possible.
1. Check scope drift, runtime output drift, carry-over readiness, and cleanup readiness before continuing or deleting a worktree.
