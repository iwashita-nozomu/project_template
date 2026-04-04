# エージェント利用ガイド

## どこから読むか

1. [agents/README.md](/mnt/l/workspace/project_template/agents/README.md)
1. [agents/canonical/README.md](/mnt/l/workspace/project_template/agents/canonical/README.md)
1. [agents/TASK_WORKFLOWS.md](/mnt/l/workspace/project_template/agents/TASK_WORKFLOWS.md)

## 入口の使い分け

- Codex / Copilot agent mode:
  - [AGENTS.md](/mnt/l/workspace/project_template/AGENTS.md)
- Claude Code:
  - [CLAUDE.md](/mnt/l/workspace/project_template/CLAUDE.md)
- GitHub Copilot custom instructions:
  - [.github/copilot-instructions.md](/mnt/l/workspace/project_template/.github/copilot-instructions.md)

## skill の使い方

- 共通 skill の正本は `.agents/skills/` にあります。
- Claude では `.claude/skills/` の mirror を使います。
- どの skill を使うか迷う場合は、まず `repo-onboarding` か `agent-orchestration` を見ます。
- 文書の置き場で迷う場合は `artifact-placement` を見ます。
- CLI 差分で迷う場合は `codex-cli`、`claude-code-cli`、`copilot-cli` を見ます。

## subagent の使い方

- Claude 専用 subagent は `.claude/agents/` にあります。
- subagent は task 固有に使い、repo 全体の正本は `agents/` 側に置きます。
- specialist を立ち上げる前に `subagent-bootstrap` を見て、必要なら run bundle を先に作ります。
