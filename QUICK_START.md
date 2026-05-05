# Quick Start
<!--
@dependency-start
responsibility Documents Quick Start for this repository.
upstream design README.md primary repository overview
upstream design AGENTS.md runtime agent entrypoint
@dependency-end
-->

このファイルは、テンプレート repo で作業を始めるための最短入口です。

## 1. 最初に読む

- [README.md](README.md)
- [documents/README.md](documents/README.md)
- [agents/workflows/README.md](agents/workflows/README.md)
- [documents/linux-wsl-host-requirements.md](documents/linux-wsl-host-requirements.md)
- [documents/template-bootstrap.md](documents/template-bootstrap.md)
- [documents/conventions/README.md](documents/conventions/README.md)
- [documents/coding-conventions-python.md](documents/coding-conventions-python.md)
- [documents/cpp-build-layout.md](documents/cpp-build-layout.md)

実験を扱う場合は追加で次を見ます。

- [agents/workflows/experiment-workflow.md](agents/workflows/experiment-workflow.md)
- [agents/workflows/research-workflow.md](agents/workflows/research-workflow.md)
- [documents/experiment-registry.md](documents/experiment-registry.md)
- [experiments/README.md](experiments/README.md)

agent を使う場合は次を見ます。

- [agents/README.md](agents/README.md)
- [documents/AGENTS_COORDINATION.md](documents/AGENTS_COORDINATION.md)

## 2. 作業の始め方

- 既定の統合先は `main` です。
- 短期 branch は必要なときだけ切り、長期の分岐運用は避けます。
- branch 側で file 構成を変えた場合は、`agents/workflows/main-integration-workflow.md` を見て integration worktree で戻します。
- 変更の前に、対象ディレクトリと必要な更新を先に決めます。
- Python と Markdown は常に対象に含まれる前提で確認します。

template から起こした直後に repo 名や bare remote 名を変えるなら wrapper から始めます。

```bash
bash scripts/start_repository.sh --project-slug your-project --display-name "Your Project"
```

最低限の確認:

```bash
git status --short
make ci-quick
python3 -m pyright
```

`make ci-quick` を host で直接流す場合は `docker/requirements.txt` 相当の Python tool が入っている前提です。canonical runtime は container なので、迷う場合は devcontainer か `docker/` 配下の runner から実行します。

## 3. 実装前の確認

- `documents/conventions/README.md` と `documents/coding-conventions-python.md` を先に見ます。
- agent workflow を使う変更なら `agents/workflows/README.md` と `agents/canonical/CODEX_WORKFLOW.md` を確認します。

```bash
make ci-quick
make docs-check
python3 -m pytest tests/ -q --tb=short
pipdeptree --warn fail
```

フルチェック:

```bash
make ci
```

## 4. よく使うコマンド

```bash
make ci-quick
make ci
make docs-check
make experiment-check
make docker-build-check
bash tools/run_comprehensive_review.sh
```

## 5. 実験の基本

- 実験コードは `experiments/<topic>/` に置きます。
- topic の正本 entrypoint と formal command は `experiments/registry.toml` に置きます。
- 新しい topic は `python3 tools/experiments/create_experiment_topic.py <topic>` で作ります。
- 実行ごとの生成物は `experiments/<topic>/result/<run_name>/` に置きます。
- 1 回の実験 report は `experiments/report/<run_name>.md` に置きます。
- server で formal run を回すときは `tools/experiments/run_managed_experiment.py --topic <topic> --use-registered-command formal` で `run_manifest.json` と `run.log` を残します。
- partial run を正式結果として扱いません。
- agent に実験つき改造 loop を回させる場合は `agents/skills/experiment-change-loop.md` と `agents/templates/experiment_change_loop.md` を使います。

## 6. 環境の基本

- 共通開発環境は `docker/` を基準にします。
- host 前提は `documents/linux-wsl-host-requirements.md` を正本にします。
- container runtime の再利用 surface は `docker/packs/*.toml` と `tools/ci/run_container_pack.py` を基準にします。
- Python 依存を追加する場合は `docker/Dockerfile` と `docker/requirements.txt` を同時に更新します。
- `docker/Dockerfile` か `docker/requirements.txt` を更新したら `make docker-build-check` を流します。
- repo-wide な tool 導入案や Docker 変更では `agents/templates/environment_change_proposal.md` に triggering code requirement と blocked command を先に記録します。
- container 内では `PYTHONPATH=/workspace/python` を前提にします。
- Jupyter notebook runtime は canonical container に入れます。
- host browser から container 内 JupyterLab を使う場合は `make docker-jupyter` を実行し、`http://127.0.0.1:8888/lab?token=project-template` を開きます。port / token は `JUPYTER_HOST_PORT` と `JUPYTER_TOKEN` で変更できます。
- repo-local `.venv` は host では作らず、container 内だけ `make python-env-status` と `make python-env-prepare` を使います。
- C++ を使う場合の canonical CMake entrypoint は root `CMakeLists.txt` です。
- out-of-source build tree は `build/cpp/<profile>/`、再利用する local install tree は `.state/cpp-install/<profile>/`、再利用する local `jax.export` artifact は `.state/jax-export/<profile>/` に置きます。
- Markdown の体裁ルールは `.markdownlint.json` と `documents/conventions/common/05_docs.md` を基準にします。
- 依存棚卸しは `pipdeptree` と `deptry` を baseline にします。

Codex CLI と `docker` CLI は `docker/Dockerfile` に同梱します。コンテナ内では `codex login`、API key を使う場合は `printenv OPENAI_API_KEY | codex login --with-api-key` を使います。`safe.directory` は image build 時に `git config --global` で固定し、既定で `/workspace` と local bare remote 用の `/mnt/git/template.git`、`/mnt/git/agent-canon.git` を登録します。project-scoped Codex config の `.codex/config.toml` では `approval_policy = "never"` と `sandbox_mode = "danger-full-access"` を既定にしているので、container 内で起動した Codex も最初から full access です。`jax.export` 用には `CMAKE_GENERATOR=Ninja` を image 側で固定し、calling convention は installed JAX wheel の supported range に追従させます。

VS Code から開発コンテナへ入る場合は `.devcontainer/` を使います。compose 生成の正本は `python3 tools/ci/render_devcontainer_compose.py --pack docker/packs/default.toml` で、GPU がある host では自動で `gpus: all` を追加し、GPU が無い host では CPU-only で起動します。`/mnt/git` も host に存在するときだけ mount し、container 内から local bare remote へ push / pull できます。host `~/.codex`、`~/.config/gh`、`~/.ssh` があれば container へ mount し、`SSH_AUTH_SOCK` が有効なら `/ssh-agent` として forward します。初回 `gh auth login` と SSH host key 登録は host 側で行い、container はその state を再利用します。attach 直後には banner を出し、GPU、`/mnt/git`、host auth mount、SSH agent、Docker socket、Codex の `approval_policy` / `sandbox_mode` を表示します。前提拡張は `.vscode/extensions.json` を見ます。

```bash
docker build -t project-template -f docker/Dockerfile .
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/workspace -w /workspace \
  project-template bash
codex --version
docker --version
codex login
make python-env-status
make python-env-prepare
```

build 可否だけを確認したい場合は次です。

```bash
make docker-build-check
make docker-build-check-host-docker
make server-check
python3 tools/ci/check_jax_export_stack.py
cmake -S . -B build/cpp/dev -DPROJECT_TEMPLATE_ENABLE_CPP_SMOKE=ON
cmake --build build/cpp/dev --target project_template_cpp_smoke
ctest --test-dir build/cpp/dev --output-on-failure
python3 tools/ci/run_container_pack.py --pack docker/packs/default.toml --print-only
python3 tools/ci/run_codex_in_repo_container.py --print-only
```

## 7. 終了時の整理

```bash
git status --short
git branch --show-current
bash tools/push_origin.sh
```

- 長期に残す知見は `notes/` に寄せます。
- worktree を使った場合は、`documents/notes-lifecycle.md` を見て action log から knowledge/theme/failure へ昇格させる項目を決めます。
- repo 全体のルール変更は `documents/` に反映します。
- 短期 branch を使った場合は、統合後に削除して `main` に戻します。
