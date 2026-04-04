# Canonical Skill Registry

## Curated Skills

- `repo-onboarding`
  - unfamiliar repo の入口確認
- `agent-orchestration`
  - workflow family 選択と handoff 整理
- `artifact-placement`
  - task 文書、run artifact、repo 正本の置き分け
- `subagent-bootstrap`
  - specialist 起動、report bundle、write-scope 整理
- `static-validation`
  - lint / test / link / CI 確認
- `change-review`
  - findings-first review
- `experiment-workflow`
  - question, protocol, run, report の整理
- `critical-review`
  - fairness, overclaim, missing evidence の確認
- `environment-maintenance`
  - Docker, CI, dependency, runtime 更新
- `codex-cli`
  - Codex 用の入口と skill path
- `claude-code-cli`
  - Claude Code 用の入口と subagent path
- `copilot-cli`
  - Copilot CLI / coding agent 用の入口と注意点

## Discovery Paths

- Codex / Copilot:
  - `.agents/skills/<skill>/SKILL.md`
- Claude:
  - `.claude/skills/<skill>/SKILL.md`

## Legacy

旧 `.github/skills/` 系は `agents/legacy/github-skills-legacy/` へ退避しました。
