# Shared Runtime Surfaces

この文書は template root から見た shared runtime surface の説明です。
source of truth は `vendor/agent-canon/` にありますが、root 側では「どこが shared で、どこが repo-local か」をここで判断します。

## 目的

- runtime discovery に必要な shared surface を固定する
- root 側の entrypoint と repo-local 文書を分ける
- shared canon 変更時の導線を明確にする

## shared 側として扱うもの

- runtime discovery surface
  - `AGENTS.md`
  - `agents/`
  - `.agents/`
  - `.claude/`
  - `.codex/`
- shared workflow / review / agent helper
  - `documents/implementation-waterfall-workflow.md`
  - `documents/REVIEW_PROCESS.md`
  - `documents/AGENTS_COORDINATION.md`
  - `tools/`
- shared notes template
  - `notes/branches/`
  - `notes/failures/`
  - `notes/themes/`
  - `notes/worktrees/`

## root 側の正本として扱うもの

- template の入口文書
  - `README.md`
  - `QUICK_START.md`
  - `documents/README.md`
  - `documents/WORKFLOW_GUIDE.md`
  - `scripts/README.md`
  - `notes/README.md`
- implementation / environment 本体
  - `python/`
  - `tests/`
  - `docker/`
  - `experiments/registry.toml`
  - `experiments/<topic>/`

## 変更ルール

- shared surface を直すときは `vendor/agent-canon/` 側を編集します。
- root 側の symlink view や root copy を直接編集しません。
- root の shared surface が drift したら次を使います。

```bash
bash tools/sync_agent_canon.sh link-root
bash tools/sync_agent_canon.sh check
```

## PR 導線

- template 側から shared canon を直すときは `documents/agent-canon-pr-workflow.md`
- upstream sync の構造は `documents/agent-canon-subtree-migration.md`

## 補足

- shared surface の一覧そのものは `vendor/agent-canon/documents/SHARED_RUNTIME_SURFACES.md` を正本にします。
- この root 文書は template 利用者が判断しやすいように要約したものです。
