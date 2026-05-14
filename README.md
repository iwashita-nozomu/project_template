# Project Template
<!--
@dependency-start
responsibility Documents Project Template for this repository.
upstream design AGENTS.md agent runtime entrypoint
upstream design vendor/agent-canon/CONTAINER_OPERATIONS.md AgentCanon container and devcontainer operation rulebook
downstream design QUICK_START.md quick-start reader path
@dependency-end
-->

> [!IMPORTANT]
> MCP server は起動成功率が低めです。MCP 前提の作業では、起動している前提で進めず、最初に接続状態と利用可否を確認してください。

> [!IMPORTANT]
> subagent と skill の起動を甘くしないでください。task が subagent / skill を要求する場合は、parent の手作業や暗黙 fallback で代替せず、必要 surface を明示して機械的に起動してください。未起動なら、その事実を最初に確認してから進めます。

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
├── AGENTS.md, CLAUDE.md              # agent runtime entrypoint。AgentCanon submodule pin への symlink
├── Makefile                          # 日常 check / bootstrap / validation の短い入口
├── pyproject.toml                    # Python project metadata と tool 設定
├── CMakeLists.txt                    # C++ を使う場合の root entrypoint
├── python/                           # Python 実装本体
├── tests/                            # pytest と runtime/tooling のテスト
├── documents/                        # repo-local index + shared policy symlinks + active contracts
├── notes/                            # 実験・調査・運用で育てる知見とテーマ別メモ
├── references/                       # 外部仕様や参照資料など、正本ではない補助資料
├── agents/                           # shared agent canon の root view。vendor への symlink
├── .agents/, .claude/, .codex/       # Codex / Claude / shared agent runtime view
├── vendor/agent-canon/               # shared agent canon の Git submodule pin
├── tools/                            # shared automation view。vendor への symlink
├── scripts/                          # repo-local bootstrap 専用 script
├── docker/                           # canonical container と runtime pack の元設定
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
  - repo-local index、AgentCanon-owned shared policy symlink、template-owned active contract、project-owned design doc が混在します。
  - `documents/README.md` は repo-local 目次です。shared workflow / coding / review policy は AgentCanon symlink、bootstrap / host / server contract は template または derived repo の regular file として扱います。
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
  - `$start-repository` skill は `scripts/start_repository.sh` を呼び、その wrapper が clean clone では init 前の `make agent-canon-ensure-latest`、`scripts/init_from_template.sh`、必要な post-commit validation をまとめます。`--force` を init に渡すと wrapper preflight は block 扱いで skip し、dirty override を邪魔しません。
- `docker/`
  - 共通開発環境、runtime pack、nested Codex profile の定義です。
  - host / devcontainer / nested Codex で同じ runtime 前提を使うため、Dockerfile、requirements、pack toml をここに集めます。
  - notebook runtime と container-only `.venv` policy もここを基準にします。
- `experiments/`
  - 実験コード、run ごとの生成物、report を置く場所です。使わないプロジェクトでは空でも構いません。
  - topic 一覧は `experiments/registry.toml`、topic template は `experiments/_template/`、run report は `experiments/report/` に置きます。
- `python/`
  - 実装本体、共通 runtime、テスト対象コードの主置き場です。
- `tests/`
  - pytest ベースのテストを置く場所です。
  - `tests/agent_tools/` と `tests/tools/` は AgentCanon-owned mirror test、`tests/project/` や package-specific tests は project-local implementation test です。

### Bootstrap と Validation の入口

- `make start-repository ARGS='--project-slug your-project --display-name "Your Project"'`
  - clone 直後の推奨入口です。内部で `scripts/start_repository.sh` を呼びます。
- `bash scripts/start_repository.sh --validate-only`
  - init 変更を commit したあと、`agent-canon` submodule pin、fresh clone、quick CI をまとめて確認します。
- `make agent-canon-ensure-latest`
  - `vendor/agent-canon/` submodule pin を configured `agent-canon` remote の `main` と揃えます。
- `make agent-canon-update-plan`
  - 派生 repo から `agent-canon` だけ更新するときの route を read-only で確認します。
- `make agent-canon-update`
  - 派生 repo から `agent-canon` だけ更新します。内部では `ensure-latest` を使います。
- `make agent-canon-merge-main`
  - `vendor/agent-canon/` の current branch に GitHub `main` を merge します。派生 repo 側で shared canon を直した branch は、このあと GitHub に push して AgentCanon PR を開きます。
- `make agent-checks`
  - shared surface、skill mirror、agent runtime alignment、research perspective smoke を確認します。
- `make ci-quick`
  - docs、experiment registry、pytest、pyright、pydocstyle を流します。canonical runtime は container で、host で直接流す場合は `docker/requirements.txt` 相当の Python tool が入っている前提です。

## 基本方針

- 既定の統合先は `main` です。恒常的な複数 branch 運用はしません。
- 短期 branch は必要なときだけ切り、整理が済んだら `main` に戻します。
- branch 側で file 構成を変えた場合は、`agents/workflows/main-integration-workflow.md` の integration worktree 手順で `main` へ戻します。
- tracked tree に残す durable state は current tree head の canonical path だけです。旧実装、移行用の別経路、`*_old`、`*_copy`、dated snapshot、backup file、古い説明を残した文書を tracked tree に置きません。
- 実装を変えたら、その実装を説明する README、guide、workflow、規約文書も同じ変更で最新実装に合わせます。古い挙動の説明を追記で温存せず、不要になった記述は削除または正本へ置換します。
- 大規模改修、rename、構成変更のあとには、旧実装 path、旧 helper 名、旧文書 path への参照を README、guide、workflow、規約文書、script help から除去し、reader が最新 surface 以外に誘導されない状態までそろえます。
- `documents/` には正本だけを置きます。履歴説明や日付付きの途中報告は置きません。
- 実装変更では、必要なテストと文書更新を同じ変更でそろえます。
- 実験は 1 回の run を fresh 実行として扱い、途中停止 run を正式結果として継ぎ足しません。
- Python の静的解析とテスト、Markdown の体裁とリンク確認を日常運用に含めます。
- 標準の観測・依存棚卸し用として `psutil`、`pipdeptree`、`deptry`、`snakeviz` を baseline に含めます。
- repo-local `.venv` は host では作らず、container 内だけ `python3 tools/ci/python_env_policy.py --create` で `.venv` を許可します。`venv/` や `env/` などの別名 path は使いません。

shared agent canon は `vendor/agent-canon/` の Git submodule pin として参照します。clone 時は submodule も取得し、root の symlink / copy surface はその pin を runtime view として参照します。ownership と surface 種別は [SHARED_RUNTIME_SURFACES.md](vendor/agent-canon/documents/SHARED_RUNTIME_SURFACES.md) を正本にし、`.github/workflows/agent-coordination.yml` と `.github/PULL_REQUEST_TEMPLATE/agent_canon.md` は symlink ではなく vendor 正本から同期する root copy として扱います。Copilot 設定の共有正本は `vendor/agent-canon/documents/github-copilot-configuration.md` です。

## Clone And AgentCanon Update

新規 clone は submodule 込みで取得します。

```bash
git clone --recurse-submodules <template-url> <repo>
cd <repo>
```

submodule なしで clone した場合、または `vendor/agent-canon/` が空の場合は次で復旧します。

```bash
git submodule sync vendor/agent-canon
git submodule update --init --recursive vendor/agent-canon
bash tools/sync_agent_canon.sh check
```

AgentCanon の URL や branch 情報が `.gitmodules` と submodule config でずれた場合は `git submodule sync vendor/agent-canon` を先に実行します。submodule worktree が stale / detached / local-only commit を含む場合は、親 repo の tree diff ではなく `vendor/agent-canon/` の branch / status を確認します。local commit がある branch は `bash tools/update_agent_canon.sh merge-main-into-current` で GitHub `main` を取り込んでから GitHub へ push し、AgentCanon PR にします。

AgentCanon の更新順序は、AgentCanon repo を更新して push / PR merge、template の `vendor/agent-canon` pin 更新、`bash tools/sync_agent_canon.sh link-root`、validation、template commit / push です。`.gitmodules` は template runtime contract の一部なので、AgentCanon URL や branch に関わる PR では必ず確認します。GitHub `origin/main`、template `origin/main`、local `/mnt/git` mirror は別の remote なので、PR や closeout ではそれぞれの SHA を混同しません。

## まず読むもの

- `QUICK_START.md`
- `documents/template-bootstrap.md`
- `documents/README.md`
- `documents/linux-wsl-host-requirements.md`
- `documents/repository-audit-checklist.md`
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
1. 変更前に `make ci-quick` を流して、Python と Markdown の基準が壊れていないことを確認します。
1. 実装、実験コード、文書、必要なら `docker/` を更新します。
1. 仕上げに `make ci` か必要な個別チェックを流します。
1. 長期に残す判断や実験知見は `notes/` に移し、正本ルールは `documents/` に反映します。

## 新規 clone 直後の最短手順

```bash
bash scripts/start_repository.sh --project-slug your-project --display-name "Your Project"
git add -A
git commit -m "chore: initialize project from template"
bash scripts/start_repository.sh --validate-only
```

初期化時の AgentCanon 正本は GitHub submodule です。project-local bare repo は新規運用では使いません。shared canon の差分は `vendor/agent-canon/` 内の GitHub branch に commit し、AgentCanon PR で戻します。

最短 runbook は `documents/template-bootstrap.md`、notes を育てる方針は `vendor/agent-canon/documents/notes-lifecycle.md` を見ます。

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
make clean-generated
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

`make clean-generated` は ignored な `build/`、`logs/`、`reports/`、pytest / ruff cache、`__pycache__`、devcontainer generated compose だけを消します。template として残す tracked product file は消しません。

## Docker で Codex を使う

AgentCanon を持つ repo の container / devcontainer 境界は
[CONTAINER_OPERATIONS.md](vendor/agent-canon/CONTAINER_OPERATIONS.md) を先に見ます。
`docker/Dockerfile` は project runtime、shared `.devcontainer/` は Codex / GitHub CLI /
host mount などの agent ergonomics を持ちます。template 固有の実装 runbook は
[docker/README.md](docker/README.md) です。

Jupyter notebook runtime は workspace mount 後の setup で導入します。host browser から使う場合は `make docker-jupyter` を実行し、runner が `docker/install_python_dependencies.sh` を通してから JupyterLab を起動します。既定では `http://127.0.0.1:8888/lab?token=project-template` を開きます。host port は `JUPYTER_HOST_PORT=8890`、token は `JUPYTER_TOKEN=my-token` のように上書きできます。host 側では repo-local `.venv` を作らず、devcontainer や nested Codex など container 内でだけ `make python-env-status` と `make python-env-prepare` を使って `.venv` を用意します。

Dockerfile、requirements、Python installer、runtime pack のいずれかを変えたら
`bash tools/docker_dependency_validator.sh` を先に通します。image build や pack smoke に
影響する変更では `make docker-build-check` も通します。ローカルに `docker` / `podman` が
ない場合は、GitHub Actions の `Docker Build` workflow を使います。

repo-wide な tool 導入案や Docker 変更では `agents/templates/environment_change_proposal.md` に triggering code requirement、blocked command、Docker 影響、validation、rollback を残します。

project-scoped Codex config の正本は `.codex/config.toml` です。template 既定では `approval_policy = "never"` と `sandbox_mode = "danger-full-access"` を入れているので、container 内で起動した Codex も最初から full access 前提です。

VS Code の dev container は `.devcontainer/` から起動します。compose 生成、mount、
auth reuse、post-create、attach status の詳細は `CONTAINER_OPERATIONS.md` と
`docker/README.md` に寄せます。

container 内では `PYTHONPATH=/workspace/python` を前提にします。
C++ を使うときの canonical entrypoint は root [CMakeLists.txt](CMakeLists.txt) です。helper module は [cmake/README.md](cmake/README.md)、layout と artifact reuse policy は [cpp-build-layout.md](vendor/agent-canon/documents/cpp-build-layout.md) を見ます。

```bash
docker build -t project-template -f docker/Dockerfile .
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/workspace -w /workspace \
  project-template bash
bash .devcontainer/post-create.sh /workspace
codex --version
gh --version
docker --version
```

container 内から `docker build` / `docker run` を行う場合は、上のように host の Docker socket を渡すか、別 daemon を用意します。

build 確認だけを行う場合は次です。

```bash
make docker-build-check
make docker-build-check-host-docker
make server-check
cmake -S . -B build/cpp/dev
cmake --build build/cpp/dev
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
