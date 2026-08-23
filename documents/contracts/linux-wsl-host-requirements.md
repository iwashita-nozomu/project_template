<!--
@dependency-start
contract policy
responsibility Documents Linux / WSL host requirements for the parent project.
upstream design ../design/docker-zero-build-environment.md parent Docker boundary
@dependency-end
-->

# Linux / WSL Host Requirements

この文書は `project_template` と派生 repo の host 前提を定めます。対象は Linux と
WSL2 です。AgentCanon の tool runtime は別 repository の standalone bootstrap が
管理するため、この契約は AgentCanon の source checkout や常駐 container を要求しません。

## 必須

- Linux filesystem 上で作業できること
- `git`、`python3`、`cmake`、`rg` が使えること
- project Docker を使う場合は `docker version` または `podman version` が通ること
- workspace の正本 path が決まっていること

## 推奨

- WSL2 では repo、Docker state、build cache を Linux filesystem 側に置く
- `git config user.name` と `git config user.email` を設定する
- GitHub CLI は host 側で認証し、credential を project container に渡さない
- Docker daemon が rootful か rootless かに依存する手順を書かない
- AgentCanon 編集時だけ、parent repo 配下の ignored
  `workspace/agent-canondevelop/<qualified-task>/agent-canon` を使う

## WSL2

repo は `/home/...` など Linux filesystem 側に置くことを推奨します。
`/mnt/c/...` は I/O、permission、symlink、case sensitivity の差があるため、
正本 workspace と Docker build context には使いません。Docker Desktop 連携を使う
場合でも、project source は Linux 側 path を既定にします。

## Project Docker

Project の `docker/Dockerfile` と test runner が project dependency、build、test を
所有します。GPU は project の明示的な Docker 実行時オプションでのみ渡し、既定では
CPU-only とします。AgentCanon tool runtime と project image は別の責務であり、相互に
`test/` や build directory を mount しません。

```bash
docker version
bash docker/run-tests.sh --tag project-template:host-check
```

## AgentCanon の任意利用

AgentCanon が必要な task だけ standalone checkout から次を実行します。

```bash
ROOT="$PWD"
TASK="<qualified-task>"
CANON="$ROOT/workspace/agent-canondevelop/$TASK/agent-canon"
RUNTIME="$ROOT/workspace/agent-canon-runtime/$TASK"
cd "$CANON"
COMMON=(--control-parent-root "$ROOT" --runtime-root "$RUNTIME")
./bootstrap.sh "${COMMON[@]}" install
./bootstrap.sh "${COMMON[@]}" start
./bootstrap.sh "${COMMON[@]}" target add --root "$ROOT" --mode read-only
```

`codex prepare` / `codex launch`、eval collect、eval sync は AgentCanon の契約に従います。
ログと eval は external runtime spool に置き、認可された場合だけ
[`agent-canon-log`](https://github.com/iwashita-nozomu/agent-canon-log) へ公開します。
終了時は runtime を stop/uninstall し、上記の task clone と runtime directory を削除します。

## 初期確認

```bash
uname -a
python3 --version
git --version
cmake --version
docker version
git status --short
bash test/testrunner.sh
```

## Related

- [README.md](../README.md)
- [QUICK_START.md](../../QUICK_START.md)
- [Docker environment boundary](../design/docker-zero-build-environment.md)
- [Server host contract](server-host-contract.md)
