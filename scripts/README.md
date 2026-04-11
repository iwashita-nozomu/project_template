# scripts

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

- [init_from_template.sh](/mnt/l/workspace/project_template/scripts/init_from_template.sh)
  - clone 直後に project slug、display name、bare remote 名、project-local `agent-canon` bare repo などを初期化します。
- [start_repository.sh](/mnt/l/workspace/project_template/scripts/start_repository.sh)
  - `$start-repository` skill から呼ぶ token-efficient wrapper です。
  - 既定では dry-run、初期化、`make agent-canon-ensure-latest` までを 1 command にまとめます。
  - init 変更を commit したあとは `--validate-only` で `make fresh-clone-check` と `make ci-quick` まで流します。
  - project-local `agent-canon` bare repo の seed、proposal branch 準備、remote 設定は `tools/update_agent_canon.sh register-local-bare` へ委譲します。

## 参照先

- [tools/README.md](/mnt/l/workspace/project_template/tools/README.md)
- [documents/tools/README.md](/mnt/l/workspace/project_template/documents/tools/README.md)
- [documents/SHARED_RUNTIME_SURFACES.md](/mnt/l/workspace/project_template/documents/SHARED_RUNTIME_SURFACES.md)
