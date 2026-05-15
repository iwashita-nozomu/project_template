# Docker Runtime
<!--
@dependency-start
responsibility Documents repo-local Docker runtime operation.
upstream design ../vendor/agent-canon/CONTAINER_OPERATIONS.md defines container ownership boundaries.
upstream implementation Dockerfile defines the project runtime image.
upstream implementation packs/default.toml defines the default runtime pack.
downstream implementation ../.github/workflows/docker-build.yml validates Docker packs in CI.
@dependency-end
-->

`docker/` は、この template の共通開発環境と container runtime 運用の正本です。
単に `docker build` を置くだけでなく、build / smoke / workspace mount / nested Codex を pack と profile で再利用できる形にします。

host 側の前提は [linux-wsl-host-requirements.md](../documents/linux-wsl-host-requirements.md) を正本にします。

## Primary Files

- `Dockerfile`
  - canonical container image 定義です。
- `requirements.txt`
  - repo-wide の Python 依存です。
- `install_python_dependencies.sh`
  - workspace mount 後に `requirements.txt` を install します。
- `register_safe_directories.sh`
  - mount 済み workspace と `vendor/*` を Git safe.directory に登録します。
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
runtime pack は `docker/packs/*.toml` に置き、container runtime の唯一の正本にします。devcontainer も repo-defined container runner も同じ pack と shared helper から派生させます。
runtime pack には次を 1 つの spec としてまとめます。

- Dockerfile path
- build context
- optional build target
- 一時 image tag
- smoke command 群
- runtime env / mounts / workdir

既定 pack:

- `docker/packs/default.toml`
- `docker/packs/default-host-docker.toml`

この repo の default pack は `PYTHONPATH=/workspace/python` を runtime env として持ちます。devcontainer と repo-defined container runner は同じ pack env を読むため、VS Code の Jupyter kernel と container smoke は同じ import root を使います。

主な入口:

- `python3 tools/ci/run_container_pack.py`
  - pack 定義から build と smoke を実行します。
- `python3 tools/ci/run_in_repo_container.py`
  - pack 定義から repo workspace を mount した container command を実行します。
- `python3 tools/ci/run_repo_program.py`
  - Python file、shell script、workspace binary、plain command を 1 つの入口で container 実行し、先に environment check も流します。
- `python3 tools/ci/run_python_in_dockerfile.py`
  - Python file path と rule に基づいて適切な pack で実行します。
- `python3 tools/ci/run_codex_in_repo_container.py`
  - repo を mount した canonical container 内で nested Codex を起動します。
- `python3 tools/ci/render_devcontainer_compose.py`
  - devcontainer 用の compose を canonical pack から生成します。

## Nested Codex

`run_codex_in_repo_container.py` は、repo の canonical runtime を build し、その中で `codex` を起動する入口です。
実行 profile の正本は `docker/codex-container-profiles.toml` です。
project-scoped Codex config の正本は `.codex/config.toml` で、template 既定では `approval_policy = "never"` と `sandbox_mode = "danger-full-access"` を使います。つまり container 内で起動した Codex も、`jax_solver_util` と同じく最初から full access 前提です。

既定の挙動は次です。

- `default` profile を使う
- host の `uid:gid` を container に渡す
- `HOME=/workspace/.state/nested-codex/<profile>` を使う
- host の `~/.codex` を `"$HOME/.codex"` として直接 mount する
- repo の `.codex/config.toml` から full-access default を読む
- host の `~/.gitconfig` と `~/.git-credentials` があれば持ち込む
- `SSH_AUTH_SOCK` があれば forward する

よく使う例:

```bash
python3 tools/ci/run_codex_in_repo_container.py --list-profiles
python3 tools/ci/run_codex_in_repo_container.py --print-only
python3 tools/ci/run_codex_in_repo_container.py
python3 tools/ci/run_codex_in_repo_container.py --profile host-docker
python3 tools/ci/run_codex_in_repo_container.py --share-host-codex-home
python3 tools/ci/run_codex_in_repo_container.py --no-seed-host-codex --forward-env OPENAI_API_KEY
```

## Repo Program Runner

`run_repo_program.py` は、repo 内 program を container で回す入口を 1 つにまとめた wrapper です。
次を同じ書式で扱います。

- Python file
- shell script
- workspace binary
- plain command

既定では target 実行前に軽量 environment check も実行します。

よく使う例:

```bash
python3 tools/ci/run_repo_program.py tools/ci/check_jax_export_stack.py
python3 tools/ci/run_repo_program.py tools/ci/check_docker_build.sh -- --pack docker/packs/default.toml
python3 tools/ci/run_repo_program.py python3 -- --version
python3 tools/ci/run_repo_program.py --skip-env-check --print-only cmake -- --version
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
bash tools/docker_dependency_validator.sh
python3 tools/ci/run_python_in_dockerfile.py docker/Dockerfile tools/docs/check_markdown_math.py -- README.md
```

## Python Environment Rule

この template は repo-local virtual environment を作りません。
canonical environment は Docker image、container 内 `.venv` policy、workspace mount 後の `docker/install_python_dependencies.sh` です。

禁止事項:

- host runtime で `python -m venv`、`virtualenv`、`conda create`、`uv venv`、`pipenv`、`poetry env` による repo-local env を作る
- `venv/`、`env/`、`.conda/`、`conda-env/` を workspace に作る

container runtime で `.venv` が必要な場合は、canonical policy tool だけを使います。

```bash
python3 tools/ci/python_env_policy.py --runtime container --create
```

環境 drift check は Python に依存しない次の入口を使います。

```bash
bash tools/docker_dependency_validator.sh
```

## Docker In Docker

この template が同梱するのは `docker` CLI だけです。
container 内から `docker build` / `docker run` を行う場合は、host の Docker socket を mount するか、別 daemon を使います。

host socket 前提の pack は `docker/packs/default-host-docker.toml` です。

```bash
python3 tools/ci/run_container_pack.py --pack docker/packs/default-host-docker.toml
python3 tools/ci/run_codex_in_repo_container.py --profile host-docker
```

`safe.directory` は `docker/register_safe_directories.sh` で登録します。image build 時には `/workspace` を登録し、dev container や smoke test では mount 済み workspace の `vendor/*` も動的に登録します。`/mnt/git` は host に存在するときだけ shared devcontainer が mount する互換 path で、Dockerfile には固定しません。

repo-defined container runner でも、host `~/.codex` が存在するときは `/root/.codex` へ自動 mount します。対象は少なくとも次です。

- `python3 tools/ci/run_in_repo_container.py`
- `python3 tools/ci/run_repo_program.py`
- `python3 tools/ci/run_container_pack.py`
- `python3 tools/ci/run_python_in_dockerfile.py`

つまり、dev container に入らず `make docker-run ARGS='...'` や `python3 tools/ci/run_repo_program.py ...` を使う場合でも、container 内の `~/.codex` は host state をそのまま使います。

## VS Code Dev Container

`.devcontainer/devcontainer.json` は 1 枚の generated Docker Compose file を使います。起動前に `.devcontainer/generate-runtime-compose.sh` を走らせますが、実体の生成は `python3 tools/ci/render_devcontainer_compose.py --pack docker/packs/default.toml --output .devcontainer/docker-compose.generated.yml` です。つまり devcontainer も repo-defined container runner も `docker/packs/default.toml` と `tools/ci/container_runtime.py` を同じ source にします。host を見て次を自動切替します。

- NVIDIA GPU が見えるとき:
  - `gpus: all` を追加
- GPU が見えないとき:
  - CPU-only のまま起動
- `/mnt/git` が存在するとき:
  - `/mnt/git:/mnt/git` を bind mount
  - local bare remote への push/pull を container 内から継続できる
- `/mnt/git` が無いとき:
  - mount しない
  - dev container 自体は CPU/GPU 判定だけでそのまま起動する
- host `~/.codex` が存在するとき:
  - `${HOME}/.codex:/root/.codex` を bind mount
  - dev container 内の Codex auth / config は host と同じ state を使う
- host `~/.codex` が無いとき:
  - mount しない

そのため、template を clone したディレクトリでも、GPU なし環境で dev container が落ちにくくなります。

VS Code で attach した直後には `.devcontainer/post-attach.sh` を実行し、少なくとも次を banner で表示します。

- GPU の有無
- `/mnt/git` mount の有無
- host `~/.codex` mount の有無
- Docker socket mount の有無
- Codex の `approval_policy` と `sandbox_mode`
- `PYTHONPATH`

VS Code の前提拡張は `.vscode/extensions.json` で human-facing に推薦し、devcontainer 内では `.devcontainer/devcontainer.json` の `customizations.vscode.extensions` で同じ core extension を自動 install します。Python interpreter は `/usr/bin/python3`、Jupyter notebook root は `/workspace` に固定します。

- `ms-python.python`
- `ms-toolsai.jupyter`
- `ms-azuretools.vscode-docker`
- `ms-vscode-remote.remote-containers`
- `ms-vscode.cpptools`
- `ms-vscode.cmake-tools`

runtime 側の C/C++ 基本 tool は、すでに `docker/Dockerfile` に入っています。

- `build-essential`
- `pkg-config`
- `cmake`
- `ninja-build`

Codex CLI、Node/npm、GitHub CLI / `gh` は project runtime image には入れません。必要な場合は AgentCanon-owned `.devcontainer/post-create.sh` が workspace mount 後に導入します。

JAX と C++ の接続を `jax.export` 前提で使う場合は、canonical image に次を同梱します。

- `jax[cuda12]`
- `flatbuffers`
- `iree-base-compiler`
- `iree-base-runtime`
- `python3-dev`
- `cmake`
- `ninja-build`
- `build-essential`

template 既定では `CMAKE_GENERATOR=Ninja` を image 側で固定します。`jax.export` の calling convention は installed JAX wheel の supported range に追従させ、`python3 tools/ci/check_jax_export_stack.py` で実際の version range を確認します。この smoke は次を一度に見ます。

- `jax.export` による StableHLO export
- `iree-base-compiler` による StableHLO -> VM flatbuffer compile
- `iree-base-runtime` による `local-task` 実行
- `jaxlib/include` の XLA FFI header
- root `CMakeLists.txt` と `tests/cpp/smoke/jax_export_header_smoke.cpp` の C++ smoke

なので、現時点では Docker image 側に追加の CMake setup は不要です。必要になったら compiler、debugger、language server を用途別に足します。

canonical CMake layout と build artifact の再利用方針は [cpp-build-layout.md](../vendor/agent-canon/documents/cpp-build-layout.md) を見ます。要点は次です。

- root `CMakeLists.txt`
  - canonical entrypoint
- `cmake/`
  - helper module
- `build/cpp/<profile>/`
  - out-of-source build tree
- `.state/cpp-install/<profile>/`
  - reusable local install tree
- `.state/jax-export/<profile>/`
  - reusable local export artifact

host に `docker` group が設定されていても、現在の shell がその group をまだ持っていない場合があります。`getent group docker` にユーザー名が出ても `id` に `docker` が無いときは、新しい login shell を開いてから `make docker-build-check` を実行します。一時確認だけなら `sg docker -c 'docker version'` で daemon 到達性を切り分けられます。

Linux / WSL2 host の前提、`/mnt/git` の扱い、workspace の置き場所は `documents/linux-wsl-host-requirements.md` を見ます。

## Standard Commands

```bash
make docker-build-check
make docker-build-check-host-docker
make server-check
make docker-shell
make docker-codex
make docker-codex-host-docker
python3 tools/ci/check_jax_export_stack.py
cmake -S . -B build/cpp/dev -DPROJECT_TEMPLATE_ENABLE_CPP_SMOKE=ON
cmake --build build/cpp/dev --target project_template_cpp_smoke
ctest --test-dir build/cpp/dev --output-on-failure
python3 tools/ci/run_container_pack.py --pack docker/packs/default.toml --print-only
python3 tools/ci/run_repo_program.py --print-only tools/ci/check_jax_export_stack.py
python3 tools/ci/run_in_repo_container.py --pack docker/packs/default.toml --shell-session --tty
```

## Update Rule

`docker/Dockerfile` や `docker/requirements.txt` を更新した変更では、次も同じ変更で見直します。

- `README.md`
- `QUICK_START.md`
- `documents/coding-conventions-project.md`
- この `docker/README.md`

必要なら `agents/templates/environment_change_proposal.md` に triggering code requirement、blocked command、影響範囲、validation、rollback を残します。
