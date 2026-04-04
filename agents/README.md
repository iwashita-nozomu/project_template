# Agent Hub

このディレクトリは、repo におけるエージェント運用の人間向け正本ハブです。
個別エージェント向けの runtime entrypoint は薄く保ち、詳細はここへ集約します。

## 正本

- [canonical/README.md](/mnt/l/workspace/project_template/agents/canonical/README.md)
  - 共通レイアウトと正本の置き場
- [agents_config.json](/mnt/l/workspace/project_template/agents/agents_config.json)
  - チーム定義と write policy
- [TASK_WORKFLOWS.md](/mnt/l/workspace/project_template/agents/TASK_WORKFLOWS.md)
  - workflow family と task 選択
- [COMMUNICATION_PROTOCOL.md](/mnt/l/workspace/project_template/agents/COMMUNICATION_PROTOCOL.md)
  - handoff / review / escalation の正本
- [task_catalog.yaml](/mnt/l/workspace/project_template/agents/task_catalog.yaml)
  - machine-readable catalog
- [canonical/ARTIFACT_PLACEMENT.md](/mnt/l/workspace/project_template/agents/canonical/ARTIFACT_PLACEMENT.md)
  - task 文書と run artifact の置き分け
- [canonical/CLI_ENTRYPOINTS.md](/mnt/l/workspace/project_template/agents/canonical/CLI_ENTRYPOINTS.md)
  - agent ごとの入口差分と bootstrap 入口

## Runtime Entry Points

- [AGENTS.md](/mnt/l/workspace/project_template/AGENTS.md)
  - Codex / Copilot agent mode の入口
- [CLAUDE.md](/mnt/l/workspace/project_template/CLAUDE.md)
  - Claude Code の入口
- [.github/copilot-instructions.md](/mnt/l/workspace/project_template/.github/copilot-instructions.md)
  - GitHub Copilot repository instructions
- [.github/AGENTS.md](/mnt/l/workspace/project_template/.github/AGENTS.md)
  - GitHub 側の薄い入口

## Skills And Subagents

- Canonical project skills: `.agents/skills/`
- Claude compatibility mirror: `.claude/skills/`
- Claude subagents: `.claude/agents/`
- Legacy GitHub-specific artifacts: `agents/legacy/`

## 運用ルール

- 共通方針は `agents/` 配下に集約し、entrypoint へ重複記述しません。
- 新しい workflow や skill を追加するときは、まず `agents/canonical/` の文書を更新します。
- 実行環境固有の都合がある場合だけ、`AGENTS.md`、`CLAUDE.md`、`.github/copilot-instructions.md` に最小限の差分を持たせます。
