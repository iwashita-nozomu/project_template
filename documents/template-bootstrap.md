# Template Bootstrap

この文書は、`git clone <template>` 直後に新しい repo を使い始めるときの最短 runbook です。

## 1. Clone 直後

```bash
git clone <template-repo> <your-project>
cd <your-project>
```

## 2. 初期化

repo 名、表示名、bare remote 名を変える場合は次を使います。

```bash
bash scripts/init_from_template.sh \
  --project-slug your-project \
  --display-name "Your Project"
```

必要なら dry-run:

```bash
bash scripts/init_from_template.sh \
  --project-slug your-project \
  --display-name "Your Project" \
  --dry-run
```

## 3. 受け入れ確認

fresh clone と runtime surface が壊れていないことを確認します。

```bash
make fresh-clone-check
make ci-quick
```

## 4. 開発環境

- host 前提:
  - `documents/linux-wsl-host-requirements.md`
- container:
  - `docker/README.md`
- VS Code devcontainer:
  - `.devcontainer/`
- 推奨拡張:
  - `.vscode/extensions.json`

## 5. 作業開始

- agent workflow:
  - `agents/README.md`
- workflow canon:
  - `documents/WORKFLOW_GUIDE.md`
- worktree kickoff:
  - `bash tools/worktree_start.sh <branch-name> [worktree-path]`

worktree を使う場合は kickoff 後に継続ログを残します。

```bash
python3 tools/agent_tools/work_log.py \
  --kind kickoff \
  --message "references and scope confirmed" \
  --next "start implementation"
```
