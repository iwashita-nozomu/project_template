# Docker Runtime

`docker/` は、この template の共通開発環境と container runtime 運用の正本です。
単に `docker build` を置くだけでなく、build / smoke / workspace mount / nested Codex を pack と profile で再利用できる形にします。

## Primary Files

- `Dockerfile`
  - canonical container image 定義です。
- `requirements.txt`
  - repo-wide の Python 依存です。
- `packs/default.toml`
  - 既定 build / smoke pack です。
- `packs/default-host-docker.toml`
  - host Docker socket を mount して daemon 到達性も見る pack です。
- `codex-container-profiles.toml`
  - nested Codex 実行 profile の正本です。
- `python-execution-rules.toml`
  - `run_python_in_dockerfile.py` が Python file をどの pack で動かすか決める規則です。

## Runtime Pack

build と smoke は `Dockerfile` を直接たたく代わりに、runtime pack を使います。
runtime pack は `docker/packs/*.toml` に置き、次を 1 つの spec にまとめます。

- Dockerfile path
- build context
- optional build target
- 一時 image tag
- smoke command 群
- runtime env / mounts / workdir

既定 pack:

- `docker/packs/default.toml`
- `docker/packs/default-host-docker.toml`

主な入口:

- `python3 scripts/ci/run_container_pack.py`
  - pack 定義から build と smoke を実行します。
- `python3 scripts/ci/run_in_repo_container.py`
  - pack 定義から repo workspace を mount した container command を実行します。
- `python3 scripts/ci/run_python_in_dockerfile.py`
  - Python file path と rule に基づいて適切な pack で実行します。
- `python3 scripts/ci/run_codex_in_repo_container.py`
  - repo を mount した canonical container 内で nested Codex を起動します。

## Nested Codex

`run_codex_in_repo_container.py` は、repo の canonical runtime を build し、その中で `codex` を起動する入口です。
実行 profile の正本は `docker/codex-container-profiles.toml` です。

既定の挙動は次です。

- `default` profile を使う
- host の `uid:gid` を container に渡す
- `HOME=/workspace/.state/nested-codex/<profile>` を使う
- host の `~/.codex/auth.json` と `~/.codex/config.toml` があれば seed する
- host の `~/.gitconfig` と `~/.git-credentials` があれば持ち込む
- `SSH_AUTH_SOCK` があれば forward する

よく使う例:

```bash
python3 scripts/ci/run_codex_in_repo_container.py --list-profiles
python3 scripts/ci/run_codex_in_repo_container.py --print-only
python3 scripts/ci/run_codex_in_repo_container.py
python3 scripts/ci/run_codex_in_repo_container.py --profile host-docker
python3 scripts/ci/run_codex_in_repo_container.py --share-host-codex-home
python3 scripts/ci/run_codex_in_repo_container.py --no-seed-host-codex --forward-env OPENAI_API_KEY
```

## Python File Runner

`run_python_in_dockerfile.py` は、Python file を container で再現したいときの入口です。
規則の正本は `docker/python-execution-rules.toml` です。

この file では、少なくとも次を rule として持ちます。

- `dockerfile`
- `match_roots`
- `pack`
- `python_bin`
- `workdir`

よく使う例:

```bash
python3 scripts/ci/run_python_in_dockerfile.py docker/Dockerfile scripts/docker_dependency_validator.py
python3 scripts/ci/run_python_in_dockerfile.py docker/Dockerfile scripts/tools/check_markdown_math.py -- README.md
```

## Docker In Docker

この template が同梱するのは `docker` CLI だけです。
container 内から `docker build` / `docker run` を行う場合は、host の Docker socket を mount するか、別 daemon を使います。

host socket 前提の pack は `docker/packs/default-host-docker.toml` です。

```bash
python3 scripts/ci/run_container_pack.py --pack docker/packs/default-host-docker.toml
python3 scripts/ci/run_codex_in_repo_container.py --profile host-docker
```

`safe.directory` は build 時に固定しません。entrypoint が run 時の `PWD` を自動登録し、追加 path は `GIT_SAFE_DIRECTORIES` で渡します。

## Standard Commands

```bash
make docker-build-check
make docker-build-check-host-docker
make docker-shell
make docker-codex
make docker-codex-host-docker
python3 scripts/ci/run_container_pack.py --pack docker/packs/default.toml --print-only
python3 scripts/ci/run_in_repo_container.py --pack docker/packs/default.toml --shell-session --tty
```

## Update Rule

`docker/Dockerfile` や `docker/requirements.txt` を更新した変更では、次も同じ変更で見直します。

- `README.md`
- `QUICK_START.md`
- `documents/coding-conventions-project.md`
- この `docker/README.md`

必要なら `agents/templates/environment_change_proposal.md` に理由、影響範囲、validation、rollback を残します。
