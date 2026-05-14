# vendor

<!--
@dependency-start
responsibility Documents vendored shared assets in this repository.
upstream design agent-canon/documents/agent-canon-github-remote.md defines the AgentCanon canonical remote.
upstream design agent-canon/documents/SHARED_RUNTIME_SURFACES.md defines shared root views.
downstream implementation agent-canon stores the AgentCanon submodule checkout.
@dependency-end
-->

`vendor/` は、外部で管理される shared asset を、この repo に取り込む場所です。

この template では、shared agent canon の取り込み先を次に固定します。

- `vendor/agent-canon/`

原則:
- product runtime の正面入口は root `AGENTS.md` と root `.codex/` に残します
- `vendor/agent-canon/` は shared canon の Git submodule pin として扱います
- shared canon の同期は [tools/sync_agent_canon.sh](../tools/sync_agent_canon.sh) から行います
- template repo には submodule pin を残し、必要な root view は `bash tools/sync_agent_canon.sh link-root` で同期します
- root の `AGENTS.md`, `agents/`, `.agents/`, `.claude/`, `CLAUDE.md`, `.codex/`, `.devcontainer/`, `tools/`, `mcp/`, selected `notes/`, and selected `tests/` は、この submodule pin を指す shared root view にします
- shared runtime surface の ownership 正本は `vendor/agent-canon/documents/SHARED_RUNTIME_SURFACES.md` です
- `.github/workflows/agent-coordination.yml` などの GitHub path-constrained files は、この submodule pin を正本とする root 同期コピーにします

よく使うコマンド:

```bash
bash tools/sync_agent_canon.sh link-root
bash tools/sync_agent_canon.sh check
bash tools/update_agent_canon.sh plan
bash tools/update_agent_canon.sh apply
bash tools/update_agent_canon.sh merge-main-into-current
bash tools/sync_agent_canon.sh status
```

注意:
- `vendor/agent-canon/AGENTS.md` は、必要なら canon 開発 submodule 用 override としてだけ置きます
- product 全体の runtime discovery は root entrypoint に寄せます
- `check` は shared surface の drift を fail-fast で検出します
- `link-root` は shared surface の symlink と同期コピーを vendor 正本へ戻します。対象に未 commit の変更がある場合は、先に commit / stash するか、意図的な再同期だけ `AGENT_CANON_FORCE_RELINK=1` を使います
