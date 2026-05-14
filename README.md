# docomo_bt_management
<!--
@dependency-start
responsibility Provides the human-facing repository entrypoint.
upstream design vendor/agent-canon/CONTAINER_OPERATIONS.md defines Docker and devcontainer ownership boundaries.
upstream design vendor/agent-canon/documents/github-copilot-configuration.md defines GitHub Copilot discovery surfaces.
downstream implementation docker/README.md documents repo-local Docker runtime usage.
downstream implementation .github/workflows/ci.yml runs repository CI.
@dependency-end
-->

実装、実験、文書、エージェント運用を 1 つの repo で扱うためのテンプレートです。
このテンプレートは、Python 実装と Markdown 文書を必ず使う研究開発 repo を前提にしています。

この README は人間向けの入口です。エージェント向けの入口は `agents/README.md` です。

## テンプレート構造

この repo は、project 固有の実装、実験、文書、開発環境、agent runtime を同じ root から扱えるように分けています。
clone 直後にまず見る入口はこの README、agent に作業させる入口は `agents/README.md`、実際の初期化入口は `scripts/start_repository.sh` です。

```text
.
├── README.md                         # 人間向けの全体入口
├── QUICK_START.md                    # 最短の手動起動手順
├── AGENTS.md, CLAUDE.md              # agent runtime entrypoint。vendor snapshot への symlink
├── Makefile                          # 日常 check / bootstrap / validation の短い入口
├── pyproject.toml                    # Python project metadata と tool 設定
├── CMakeLists.txt                    # C++ を使う場合の root entrypoint
├── python/                           # Python 実装本体
├── tests/                            # pytest と runtime/tooling のテスト
├── documents/                        # repo-wide な規約、設計、環境文書の正本
├── notes/                            # 実験・調査・運用で育てる知見とテーマ別メモ
├── references/                       # 外部仕様や参照資料など、正本ではない補助資料
├── agents/                           # shared agent canon の root view。vendor への symlink
├── .agents/, .claude/, .codex/       # Codex / Claude / shared agent runtime view
├── vendor/agent-canon/               # shared agent canon の Git submodule pin
├── tools/                            # shared automation view。vendor への symlink
├── scripts/                          # repo-local bootstrap 専用 script
├── docker/                           # canonical container、runtime pack、devcontainer の元設定
├── .devcontainer/                    # VS Code dev container entrypoint
├── .github/                          # CI workflow と PR template
├── experiments/                      # 実験 topic、run artifact、report
├── cmake/                            # C++ helper module
├── src/, include/, lib/              # C / C++ を使う project 向けの実装置き場
├── reports/                          # 実行結果、broken link report、agent run bundle などの生成先
└── .vscode/                          # 推奨拡張など editor 補助
```

### Repo-Local と Shared Canon の境界

- `documents/`
  - 規約、設計、開発環境、contract の正本です。
  - workflow canon は置かず、project 固有の rule / contract だけをここに置きます。
- `notes/`
  - 実験や調査をまたいで残したい知見、補助メモ、テーマ整理を置きます。
  - その場限りの run log ではなく、後続作業で再利用する知識だけを残します。
- `agents/`
  - エージェントチーム定義、運用ルール、workflow canon の正本です。
  - root の `agents/` は `vendor/agent-canon/agents` への symlink です。shared workflow を直すときは `vendor/agent-canon/` 側を正本として扱います。
- `tools/`
  - shared automation、agent helper、CI/check、container runner の入口です。
  - agent helper、CI / review / validation、container runner、experiment helper、Markdown helper の実装はここに置きます。
  - root の `tools/` は `vendor/agent-canon/tools` への symlink です。project 固有の slug 置換や bare remote 初期化はここに置きません。
- `scripts/`
  - repo-local bootstrap の入口です。
  - template 固有の slug 置換、display name 置換、bare remote 初期化だけをここに置きます。
  - `$start-repository` skill は `scripts/start_repository.sh` を呼び、その wrapper が `scripts/init_from_template.sh`、repo-local AgentCanon bare seed、`make agent-canon-ensure-latest`、必要な post-commit validation をまとめます。
- `docker/`
  - 共通開発環境、runtime pack、nested Codex profile の定義です。
  - host / devcontainer / nested Codex で同じ runtime 前提を使うため、Dockerfile、requirements、pack toml をここに集めます。
- `experiments/`
  - 実験コード、run ごとの生成物、report を置く場所です。使わないプロジェクトでは空でも構いません。
  - topic 一覧は `experiments/registry.toml`、topic template は `experiments/_template/`、run report は `experiments/report/` に置きます。
- `python/`
  - 実装本体、共通 runtime、テスト対象コードの主置き場です。
- `tests/`
  - pytest ベースのテストを置く場所です。
  - shared agent/tooling の mirror test は `vendor/agent-canon/tests/` に正本があり、root `tests/` からも runtime surface として参照できます。

### Bootstrap と Validation の入口

- `make start-repository ARGS='--project-slug your-project --display-name "Your Project"'`
  - clone 直後の推奨入口です。内部で `scripts/start_repository.sh` を呼びます。
- `bash scripts/start_repository.sh --validate-only`
  - init 変更を commit したあと、`agent-canon` snapshot、fresh clone、quick CI をまとめて確認します。
- `make agent-canon-ensure-latest`
  - `vendor/agent-canon/` snapshot を configured `agent-canon` remote の `main` と揃えます。
- `make agent-canon-update-plan`
  - 派生 repo から `agent-canon` だけ更新するときの route を read-only で確認します。
- `make agent-canon-update`
  - 派生 repo から `agent-canon` だけ更新します。内部では `ensure-latest` を使います。
- `make agent-canon-merge-main`
  - `vendor/agent-canon/` の現在 branch に GitHub `main` を merge し、AgentCanon PR branch を最新化します。
- `make agent-checks`
  - shared surface、skill mirror、agent runtime alignment、research perspective smoke を確認します。
- `make ci-quick`
  - docs、experiment registry、pytest、pyright、pydocstyle を流します。

## 基本方針

- 既定の統合先は `main` です。恒常的な複数 branch 運用はしません。
- 短期 branch は必要なときだけ切り、整理が済んだら `main` に戻します。
- branch 側で file 構成を変えた場合は、`agents/workflows/main-integration-workflow.md` の integration worktree 手順で `main` へ戻します。
- `documents/` には正本だけを置きます。履歴説明や日付付きの途中報告は置きません。
- 実装変更では、必要なテストと文書更新を同じ変更でそろえます。
- 実験は 1 回の run を fresh 実行として扱い、途中停止 run を正式結果として継ぎ足しません。
- Python の静的解析とテスト、Markdown の体裁とリンク確認を日常運用に含めます。
- 標準の観測・依存棚卸し用として `psutil`、`pipdeptree`、`deptry`、`snakeviz` を baseline に含めます。

shared agent canon は `vendor/agent-canon/` の Git submodule pin を正本にします。GitHub Copilot / PR automation の発見面は `.github/PULL_REQUEST_TEMPLATE/agent_canon.md` と `vendor/agent-canon/documents/github-copilot-configuration.md` を参照します。ownership と surface 種別は `vendor/agent-canon/documents/SHARED_RUNTIME_SURFACES.md` を正本にし、root view は `bash tools/sync_agent_canon.sh link-root` で同期します。

## まず読むもの

- `QUICK_START.md`
- `documents/template-bootstrap.md`
- `documents/README.md`
- `documents/linux-wsl-host-requirements.md`
- `agents/workflows/README.md`
- `vendor/agent-canon/documents/conventions/README.md`
- `vendor/agent-canon/documents/coding-conventions-python.md`
- `vendor/agent-canon/documents/cpp-build-layout.md`
- 開発環境を触る場合は `docker/`
- host 前提を確認する場合は `documents/linux-wsl-host-requirements.md`
- 実験を行う場合は `agents/workflows/experiment-workflow.md`
- 実験 topic を作る場合は `experiments/README.md`
- topic registry を触る場合は `vendor/agent-canon/documents/experiment-registry.md`
- エージェントを使う場合は `agents/README.md`

## 日常の進め方

1. 何を変えるかを決めます。実装だけか、実験まで含むか、環境や文書更新が必要かを最初に切ります。
2. 変更前に `make ci-quick` を流して、Python と Markdown の基準が壊れていないことを確認します。
3. 実装、実験コード、文書、必要なら `docker/` を更新します。
4. 仕上げに `make ci` か必要な個別チェックを流します。
5. 長期に残す判断や実験知見は `notes/` に移し、正本ルールは `documents/` に反映します。

## 新規 clone 直後の最短手順

```bash
bash scripts/start_repository.sh --project-slug your-project --display-name "Your Project"
git add -A
git commit -m "chore: initialize project from template"
bash scripts/start_repository.sh --validate-only
```

初期化時には project-local `agent-canon` bare repo と、その repo 専用の proposal branch `canon-proposal/<project-slug>` も用意されます。shared canon の差分はこの proposal branch に push し、maintainer 側で整理して merge します。

最短 runbook は `documents/template-bootstrap.md`、notes を育てる方針は `documents/notes-lifecycle.md` を見ます。

## 実験を含むプロジェクトでの使い方

新規実験は次のような配置を基準にします。

```text
experiments/
├── registry.toml
├── report/
│   └── <run_name>.md
└── <topic>/
    ├── README.md
    ├── cases.*
    ├── experiment.*
    └── result/
        └── <run_name>/
```

- 1 回の run の report は `experiments/report/<run_name>.md`
- run ごとの生成物は `experiments/<topic>/result/<run_name>/`
- 複数 run をまたぐ知見は `notes/experiments/` または `notes/themes/`

実験方法論そのものは `agents/workflows/experiment-workflow.md` と `agents/workflows/research-workflow.md` を正本にします。
agent に実験つき改造 loop を回させる場合は `agents/skills/adaptive-improvement-loop.md` を outer loop、`agents/skills/experiment-lifecycle.md` を run 単位の分岐に使います。
server で回す実験コードの実体テンプレは `experiments/_template/`、topic 正本は `experiments/registry.toml`、topic scaffold は `tools/experiments/create_experiment_topic.py`、run metadata を残す入口は `tools/experiments/run_managed_experiment.py` です。

## よく使うコマンド

```bash
make ci-quick
make ci
make docs-check
make agent-canon-update-plan
make agent-canon-merge-main
make experiment-check
make docker-build-check
python3 -m pyright
python3 -m pytest tests/ -q --tb=short
python3 -m ruff check python tests --select D,E,F,I,UP
pipdeptree --warn fail
deptry python
make tools-help
```

## Docker と Devcontainer

`docker/Dockerfile` は project runtime image だけを定義します。Codex CLI、Node/npm、GitHub CLI、認証 mount など agent convenience は AgentCanon-owned `.devcontainer/post-create.sh` が workspace mount 後に扱います。container runtime の正本は [docker/README.md](docker/README.md) で、build / smoke は `docker/packs/*.toml` と `tools/ci/run_container_pack.py` から実行します。`jax.export` を使う前提で `python3-dev`、`cmake`、`ninja-build` も canonical image に入れ、calling convention は installed JAX wheel の supported range に追従させます。

`docker/Dockerfile` か `docker/requirements.txt` を更新した変更では、`make docker-build-check` を通して build 可否を確認します。ローカルに `docker` / `podman` がない場合は、GitHub Actions の `Docker Build` workflow を使います。

repo-wide な tool 導入案や Docker 変更では `agents/templates/environment_change_proposal.md` に triggering code requirement、blocked command、Docker 影響、validation、rollback を残します。

`safe.directory` は `docker/register_safe_directories.sh` で動的に登録します。image build 時は `/workspace` を登録し、devcontainer / smoke test では mount 済み workspace の `vendor/*` も列挙します。`/mnt/git` は互換 mount であり、Dockerfile の既定設定には焼き込みません。

project-scoped Codex config の正本は `.codex/config.toml` です。template 既定では `approval_policy = "never"` と `sandbox_mode = "danger-full-access"` を入れているので、container 内で起動した Codex も最初から full access 前提です。

VS Code の dev container は `.devcontainer/` から起動します。起動時の compose 生成は `python3 tools/ci/render_devcontainer_compose.py --pack docker/packs/default.toml` を正本にし、GPU が見える host では `gpus: all` を自動追加し、GPU が無い host では CPU-only で起動します。`/mnt/git` も host に path がある場合だけ mount し、local bare remote への push/pull を container 内から継続できます。host `~/.codex` があれば `/root/.codex` として自動 mount し、dev container 内の Codex auth / config は host と同じ state を使います。attach 直後には banner を出し、GPU、`/mnt/git`、host `~/.codex`、Docker socket、Codex の `approval_policy` / `sandbox_mode` の状態を表示します。前提拡張は `.vscode/extensions.json` にまとめています。

container 内では `PYTHONPATH=/workspace/python` を前提にします。
C++ を使うときの canonical entrypoint は root [CMakeLists.txt](CMakeLists.txt) です。helper module は [cmake/README.md](cmake/README.md)、layout と artifact reuse policy は [cpp-build-layout.md](vendor/agent-canon/documents/cpp-build-layout.md) を見ます。

```bash
docker build -t docomo_bt_management -f docker/Dockerfile .
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/workspace -w /workspace \
  docomo_bt_management bash
docker --version
```

container 内から `docker build` / `docker run` を行う場合は、上のように host の Docker socket を渡すか、別 daemon を用意します。

build 確認だけを行う場合は次です。

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

## 詳細入口

- 規約と運用: `documents/README.md`
- 補助メモ: `notes/README.md`
- エージェント運用: `agents/README.md`
- shared automation: `tools/README.md`
- repo-local bootstrap: `scripts/README.md`
