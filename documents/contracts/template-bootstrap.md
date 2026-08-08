<!--
@dependency-start
contract template
responsibility Documents Template Bootstrap for this repository.
upstream design ../../vendor/agent-canon/documents/runtime/SHARED_RUNTIME_SURFACES.md shared documents ownership policy
upstream design ../../vendor/agent-canon/documents/agent-canon/agent-canon-github-remote.md GitHub canonical remote policy
upstream design ./template-github-remote.md template GitHub canonical remote policy
@dependency-end
-->

# Template Bootstrap

この文書は、`git clone <template>` 直後に新しい repo を使い始めるときの最短 runbook です。
この root copy は template / derived repo が所有する active contract です。AgentCanon は shared tooling と seed template を提供しますが、この repo の bootstrap 手順の正本はこの regular file です。

## この文書の読み方

- この文書は、template clone 直後の初期化、受け入れ確認、開発環境、作業開始の最短手順を所有します。
- Clone 直後、初期化、受け入れ確認、開発環境、作業開始の順に読み、GitHub remote、AgentCanon submodule、root view 更新の入口を確認します。
- 新しい derived repo を作るとき、template / AgentCanon remote を確認するとき、または bootstrap 後の validation を走らせるときに読みます。
- AgentCanon は shared tooling と seed template を提供しますが、この repo の bootstrap 手順は root regular file 側の active contract です。

## 1. Clone 直後

```bash
git clone <template-repo> <your-project>
cd <your-project>
```

## 2. 初期化

repo 名、表示名、bare remote 名を変える場合は次を使います。
agent に任せる場合は `$start-repository` を指定し、この tool を呼ばせます。

```bash
bash scripts/start_repository.sh \
  --project-slug your-project \
  --display-name "Your Project"
```

必要なら dry-run:

```bash
bash scripts/start_repository.sh \
  --project-slug your-project \
  --display-name "Your Project" \
  --dry-run
```

GitHub-backed template では、`vendor/agent-canon` submodule は
`https://github.com/iwashita-nozomu/agent-canon.git` を canonical remote として使います。
`--force` を init に渡すと wrapper は agent-canon preflight を block 扱いで skip し、dirty worktree override を優先します。
AgentCanon は GitHub submodule を正本とし、初期化時に project-local `agent-canon` bare repo は作りません。

派生 repo から `agent-canon` だけ更新したいときの canonical entry は次です。

```bash
make agent-canon-update
```

同じ更新を直接呼び出す必要がある場合だけ、generic source-root dispatcher を
同等の代替として使います。両方を連続して実行しません。

```bash
PYTHONPATH=vendor/agent-canon/tools:tools python3 -m agent_tools.agent_canon_source_root exec \
  tools/update_agent_canon.sh latest
```

派生 repo 側で shared canon を直した場合は、`vendor/agent-canon/` 内で通常の GitHub branch を作って commit し、main を取り込んでから PR を出します。

```bash
git -C vendor/agent-canon switch -c canon-pr/<short-topic>
git -C vendor/agent-canon add -A
git -C vendor/agent-canon commit -m "<message>"
PYTHONPATH=vendor/agent-canon/tools:tools python3 -m agent_tools.agent_canon_source_root exec \
  tools/update_agent_canon.sh merge-main-into-current
git -C vendor/agent-canon push origin HEAD
```

AgentCanon PR merge 後に派生 repo 側へ戻り、`make agent-canon-update` で pin、root view、compiled tool rebuild、親 repo update TODO routing をまとめて更新します。

`surface_manifest` と `dependency_module_change` は generic source-root dispatcher から
canonical AgentCanon source を実行します。

```bash
PYTHONPATH=vendor/agent-canon/tools:tools python3 -m agent_tools.agent_canon_source_root exec \
  tools/agent_tools/surface_manifest.py --help
PYTHONPATH=vendor/agent-canon/tools:tools python3 -m agent_tools.agent_canon_source_root exec \
  tools/agent_tools/dependency_module_change.py --help
```

GitHub 管理では template の canonical remote を
`https://github.com/iwashita-nozomu/project_template.git` にします。`.gitmodules` の AgentCanon URL は
`https://github.com/iwashita-nozomu/agent-canon.git` にします。
PR と security 設定の正本は GitHub 側に置きます。

最低限の確認:

```bash
gh repo view <owner>/<template-repo> --json nameWithOwner,visibility,isPrivate,defaultBranchRef
gh repo view <owner>/agent-canon --json nameWithOwner,visibility,isPrivate,defaultBranchRef
git submodule status vendor/agent-canon
```

## 3. 受け入れ確認

fresh clone と runtime surface が壊れていないことを確認します。
init 変更を commit したあと、同じ tool で確認できます。

```bash
bash scripts/start_repository.sh --validate-only
```

## 4. 開発環境

- host 前提:
  - `documents/contracts/linux-wsl-host-requirements.md`
- container:
  - `docker/README.md`
- VS Code devcontainer:
  - `.devcontainer/`
- 推奨拡張:
  - `.vscode/extensions.json`

## 5. 作業開始

- agent workflow:
  - `vendor/agent-canon/agents/README.md`
- workflow canon:
  - `vendor/agent-canon/agents/workflows/README.md`
- managed repository-topic workspace:
  - AgentCanon source clones belong under `workspace/<topic-slug>/agent-canon/`.
  - Use the dependency-module lifecycle for prepare, status, merge, and cleanup;
    remove the lifecycle-owned topic directory after commit/PR and pin readback.
