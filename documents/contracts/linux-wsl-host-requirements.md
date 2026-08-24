<!--
@dependency-start
contract policy
responsibility Documents Linux / WSL host requirements for the parent project.
upstream design ../design/docker-zero-build-environment.md parent Docker boundary
@dependency-end
-->

# Linux / WSL Host Requirements

この文書は `project_template` と派生 repo の host 前提を定めます。対象は Linux と
WSL2 です。Project validation uses only the repository-owned tools and
container, so this contract does not require a secondary source checkout or
resident tool container.

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

## WSL2

repo は `/home/...` など Linux filesystem 側に置くことを推奨します。
`/mnt/c/...` は I/O、permission、symlink、case sensitivity の差があるため、
正本 workspace と Docker build context には使いません。Docker Desktop 連携を使う
場合でも、project source は Linux 側 path を既定にします。

## Project Docker

Project の `docker/Dockerfile` と test runner が project dependency、build、test を
所有します。GPU は project の明示的な Docker 実行時オプションでのみ渡し、既定では
CPU-only とします。The project image does not mount external test or build
directories.

```bash
docker version
bash docker/run-tests.sh --tag project-template:host-check
```

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
