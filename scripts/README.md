# scripts

<!--
@dependency-start
responsibility Documents repo-local bootstrap scripts and their AgentCanon boundary.
upstream design ../vendor/agent-canon/documents/github-first-module-and-devcontainer-policy.md defines GitHub-first AgentCanon update ownership.
upstream design ../vendor/agent-canon/CONTAINER_OPERATIONS.md defines Docker and devcontainer ownership boundaries.
downstream implementation init_from_template.sh initializes template-derived repository state.
downstream implementation start_repository.sh wraps initialization and validation.
downstream implementation ../tests/tools/test_start_repository_script.py verifies AgentCanon bare seeding behavior.
@dependency-end
-->

`scripts/` は repo-local bootstrap の置き場です。
shared automation は `tools/` を使います。

## ここに置くもの

- clone 直後の初期化
- project slug や display name の置換
- bare remote 名の初期化
- project-local `agent-canon` bare repo の初期 seed

## 置かないもの

- agent helper
- CI / review / validation
- Docker / container runner
- experiment helper
- Markdown 整備

それらは `tools/` に置きます。

## 現在の入口

- [init_from_template.sh](init_from_template.sh)
  - clone 直後に project slug、display name、bare remote 名、project-local `agent-canon` bare repo などを初期化します。
- [start_repository.sh](start_repository.sh)
  - `$start-repository` skill から呼ぶ token-efficient wrapper です。
  - 既定では dry-run、初期化、`make agent-canon-ensure-latest` までを 1 command にまとめます。
  - init 変更を commit したあとは `--validate-only` で `make fresh-clone-check` と `make ci-quick` まで流します。
  - project-local `agent-canon` bare repo の seed、proposal branch 準備、remote 設定は `init_from_template.sh` が行います。`tools/update_agent_canon.sh` は GitHub-first 更新 wrapper です。

## 参照先

- [tools/README.md](../tools/README.md)
- [vendor/agent-canon/documents/tools/README.md](../vendor/agent-canon/documents/tools/README.md)
- [vendor/agent-canon/documents/SHARED_RUNTIME_SURFACES.md](../vendor/agent-canon/documents/SHARED_RUNTIME_SURFACES.md)
