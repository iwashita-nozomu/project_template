# Agent Team — Entry Point

このファイルは GitHub 側の薄い入口です。team shape や role 一覧はここへ再掲しません。

## Canonical Sources

- Team definition and write policy: `agents/agents_config.json`
- Communication protocol: `agents/COMMUNICATION_PROTOCOL.md`
- Human-facing summary: `agents/README.md`
- Runtime implementation: `scripts/agent_tools/agent_team.py`
- Repo integration guide: `documents/AGENTS_COORDINATION.md`

## GitHub-Side Rules

- team summary は `agents/README.md` を読む
- role permission と handoff は canonical source を参照する
- GitHub Actions の mirror は `.github/workflows/agent-coordination.yml` を使う
- このファイルへ role 一覧や詳細 flow を複製しない
- skills や task workflows の入口は repo 内に残し、ここから辿れる状態を維持する
