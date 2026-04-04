# エージェントチーム運用の入口

この文書は薄い入口です。team shape や role 一覧はここへ再掲しません。

## 正本

- チーム定義と write policy: `agents/agents_config.json`
- agent 間のやり取り規約: `agents/COMMUNICATION_PROTOCOL.md`
- 人間向け要約: `agents/README.md`
- task workflow カタログ: `agents/TASK_WORKFLOWS.md`
- runtime 実装: `scripts/agent_tools/agent_team.py`

## 実行入口

```bash
python3 scripts/agent_tools/bootstrap_agent_run.py \
  --task "<task>" \
  --owner "<owner>" \
  --workspace-root "$PWD"
```

## repo 側のルール

- role 定義は `agents/agents_config.json` を正本にします。
- 人間向けの要約は `agents/README.md` に集約します。
- この文書と `.github/AGENTS.md` は thin entrypoint に保ちます。
- repo の既定統合先は `main` とし、agent 運用でも恒常的な branch 分割を前提にしません。
- agent workflow、task catalog、skills は削らず、入口から辿れる状態を維持します。
