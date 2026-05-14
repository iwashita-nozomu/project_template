# Quick Start

<!--
@dependency-start
responsibility Provides the short human bootstrap path for this repository.
upstream design vendor/agent-canon/CONTAINER_OPERATIONS.md defines Docker and devcontainer ownership boundaries.
upstream design vendor/agent-canon/documents/SHARED_RUNTIME_SURFACES.md defines shared root-view ownership.
downstream implementation scripts/start_repository.sh initializes template-derived repositories.
downstream implementation docker/README.md documents repo-local container usage.
@dependency-end
-->

このファイルは、テンプレート repo で作業を始めるための最短入口です。

## 1. 最初に読む

- [README.md](README.md)
- [documents/README.md](documents/README.md)
- [agents/workflows/README.md](agents/workflows/README.md)
- [documents/linux-wsl-host-requirements.md](documents/linux-wsl-host-requirements.md)
- [documents/template-bootstrap.md](documents/template-bootstrap.md)
- [documents/conventions/README.md](vendor/agent-canon/documents/conventions/README.md)
- [documents/coding-conventions-python.md](vendor/agent-canon/documents/coding-conventions-python.md)
- [documents/cpp-build-layout.md](vendor/agent-canon/documents/cpp-build-layout.md)

実験を扱う場合は追加で次を見ます。

- [agents/workflows/experiment-workflow.md](agents/workflows/experiment-workflow.md)
- [agents/workflows/research-workflow.md](agents/workflows/research-workflow.md)
- [documents/experiment-registry.md](vendor/agent-canon/documents/experiment-registry.md)
- [experiments/README.md](experiments/README.md)

agent を使う場合は次を見ます。

- [agents/README.md](agents/README.md)
- [documents/AGENTS_COORDINATION.md](vendor/agent-canon/documents/AGENTS_COORDINATION.md)

## 2. 作業の始め方

- 既定の統合先は `main` です。
- 短期 branch は必要なときだけ切り、長期の分岐運用は避けます。
- branch 側で file 構成を変えた場合は、`agents/workflows/main-integration-workflow.md` を見て integration worktree で戻します。
- 変更の前に、対象ディレクトリと必要な更新を先に決めます。
- Python と Markdown は常に対象に含まれる前提で確認します。

template から起こした直後に repo 名や bare remote 名を変えるなら次です。

```bash
bash scripts/init_from_template.sh --project-slug your-project --display-name "Your Project"
make fresh-clone-check
```

最低限の確認:

```bash
git status --short
make ci-quick
python3 -m pyright
```

## 3. 実装前の確認

- `vendor/agent-canon/documents/conventions/README.md` と `vendor/agent-canon/documents/coding-conventions-python.md` を先に見ます。
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
- C++ を使う場合の canonical CMake entrypoint は root `CMakeLists.txt` です。
- out-of-source build tree は `build/cpp/<profile>/`、再利用する local install tree は `.state/cpp-install/<profile>/`、再利用する local `jax.export` artifact は `.state/jax-export/<profile>/` に置きます。
- Markdown の体裁ルールは `.markdownlint.json` と `documents/conventions/common/05_docs.md` を基準にします。
- 依存棚卸しは `pipdeptree` と `deptry` を baseline にします。

`docker/Dockerfile` は project runtime image だけを定義します。Codex CLI、Node/npm、GitHub CLI、認証 mount は AgentCanon-owned `.devcontainer/post-create.sh` が workspace mount 後に扱います。Python 依存は image build では入れず、container 起動後に `docker/install_python_dependencies.sh` で入れます。`safe.directory` は `docker/register_safe_directories.sh` が `/workspace` と mount 済み `vendor/*` を動的に登録します。`/mnt/git` は host に存在するときだけ shared devcontainer が mount する互換 path です。

VS Code から開発コンテナへ入る場合は `.devcontainer/` を使います。compose 生成の正本は `python3 tools/ci/render_devcontainer_compose.py --pack docker/packs/default.toml` で、GPU がある host では自動で `gpus: all` を追加し、GPU が無い host では CPU-only で起動します。`/mnt/git` も host に存在するときだけ mount し、container 内から local bare remote へ push/pull できます。host `~/.codex` があれば `/root/.codex` として自動 mount し、container 内の Codex auth / config は host と同じ state を使います。attach 直後には banner を出し、GPU、`/mnt/git`、host `~/.codex`、Docker socket、Codex の `approval_policy` / `sandbox_mode` を表示します。前提拡張は `.vscode/extensions.json` を見ます。

```bash
docker build -t docomo_bt_management -f docker/Dockerfile .
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/workspace -w /workspace \
  docomo_bt_management bash
docker --version
bash docker/install_python_dependencies.sh /workspace
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
