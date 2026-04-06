# 運用者向けワークフローガイド

この文書は、Docker runtime、CI、nested Codex、Git mirror、repo-wide tool 導入を扱う利用者向けの入口です。
repo 全体の見取り図は `documents/WORKFLOW_GUIDE.md` を見てください。

## 主に触る場所

- 環境定義:
  - `docker/`
- CI 補助:
  - `scripts/ci/`
- プロジェクト全体ルール:
  - `documents/coding-conventions-project.md`
- tool inventory:
  - `documents/WORKFLOW_INVENTORY.md`
- remote execution contract:
  - `documents/remote-execution-repo-contract.md`
- remote execution templates:
  - `documents/templates/`
- Git mirror note:
  - `notes/github-mirror-procedure.md`

## runtime の準備

まず default pack を扱える状態にします。

```bash
make docker-build-check
python3 scripts/ci/run_container_pack.py --pack docker/packs/default.toml --print-only
python3 scripts/ci/run_in_repo_container.py --pack docker/packs/default.toml --shell-session --tty --print-only
python3 scripts/ci/run_codex_in_repo_container.py --list-profiles
python3 scripts/ci/run_codex_in_repo_container.py --print-only
```

host Docker socket を使う runtime を確認したいときは次です。

```bash
make docker-build-check-host-docker
python3 scripts/ci/run_container_pack.py --pack docker/packs/default-host-docker.toml --print-only
python3 scripts/ci/run_codex_in_repo_container.py --profile host-docker --print-only
```

## nested Codex の既定

この template の nested Codex wrapper は次を既定にします。

- host の `uid:gid` を container に渡す
- `HOME=/workspace/.state/nested-codex/<profile>` を使う
- host の `~/.codex/auth.json` と `~/.codex/config.toml` があれば seed する
- host の `~/.gitconfig` と `~/.git-credentials` があれば持ち込む
- `SSH_AUTH_SOCK` があれば forward する

そのため、workspace が root 所有で汚れる risk を下げつつ、次の agent が同じ repo ルールで作業を継続しやすくなります。

## Git mirror を使う前提

mirror を使う場合の template note は `notes/github-mirror-procedure.md` です。
この repo 自体は mirror hook を同梱しません。host ごとの実 remote、SSH key、hook path は環境依存だからです。

ただし、次は必須で文書に残します。

- `origin` と mirror remote の関係
- bare repo hook の場所
- 前提 credential
- 失敗時の確認コマンド

## Remote Execution 契約

この template は remote execution の orchestration 実装を同梱しませんが、repo 側の契約文書は先に揃えます。
実行 host や control plane を別 repo / 別 server で持つ場合は、少なくとも次を正本にします。

- `documents/remote-execution-repo-contract.md`
- `documents/templates/remote_execution_repo.template.toml`
- `documents/templates/remote_execution_target.template.toml`

repo 側では Docker pack、artifact root、commit 解決方針を固定し、host 固有の接続情報は template から派生した外部設定へ逃がします。

## repo-wide な tool 導入

repo-wide tool を追加するときは `agents/templates/environment_change_proposal.md` を使い、次を決めてから実装します。

- 何の workflow を支えるのか
- host / Docker / CI のどこを更新するのか
- `docker/Dockerfile` と `docker/requirements.txt` の更新要否
- validation plan
- rollback plan

## close 条件

- `docker/` と `scripts/ci/` の変更が同期している
- `make ci` が通るか、未実行理由が説明できる
- `make docker-build-check` 系の結果が説明できる
- nested Codex や mirror を扱う場合は README / note が更新されている
- commit と push が完了している
