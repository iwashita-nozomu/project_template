# vendor

`vendor/` は、外部で管理される shared asset を、この repo に snapshot として取り込む場所です。

この template では、shared agent canon の取り込み先を次に固定します。

- `vendor/agent-canon/`

原則:
- product runtime の正面入口は root `AGENTS.md` と root `.codex/` に残します
- `vendor/agent-canon/` は shared canon の subtree snapshot として扱います
- shared canon の同期は [scripts/sync_agent_canon.sh](/mnt/l/workspace/project_template/scripts/sync_agent_canon.sh) から行います

よく使うコマンド:

```bash
bash scripts/sync_agent_canon.sh add git@github.com:<org>/agent-canon.git
bash scripts/sync_agent_canon.sh pull
bash scripts/sync_agent_canon.sh push
bash scripts/sync_agent_canon.sh status
```

注意:
- `vendor/agent-canon/AGENTS.md` は、必要なら canon 開発 subtree 用 override としてだけ置きます
- product 全体の runtime discovery は root entrypoint に寄せます
