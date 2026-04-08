# Project Template

実装、実験、文書、エージェント運用を 1 つの repo で扱うためのテンプレートです。
このテンプレートは、Python 実装と Markdown 文書を必ず使う研究開発 repo を前提にしています。

この README は人間向けの入口です。エージェント向けの入口は `agents/README.md` です。

## このテンプレートに残すもの

- `documents/`
  - 規約、設計、開発環境、実験手法の正本です。
- `notes/`
  - 実験や調査をまたいで残したい知見、補助メモ、テーマ整理を置きます。
- `agents/`
  - エージェントチーム定義、運用ルール、workflow の正本です。
- `scripts/`
  - チェック、整形、補助運用の入口です。
- `docker/`
  - 共通開発環境、runtime pack、nested Codex profile の定義です。
- `experiments/`
  - 実験コード、run ごとの生成物、report を置く場所です。使わないプロジェクトでは空でも構いません。
- `python/`
  - 実装本体、共通 runtime、テスト対象コードの主置き場です。
- `tests/`
  - pytest ベースのテストを置く場所です。

## 基本方針

- 既定の統合先は `main` です。恒常的な複数 branch 運用はしません。
- 短期 branch は必要なときだけ切り、整理が済んだら `main` に戻します。
- `documents/` には正本だけを置きます。履歴説明や日付付きの途中報告は置きません。
- 実装変更では、必要なテストと文書更新を同じ変更でそろえます。
- 実験は 1 回の run を fresh 実行として扱い、途中停止 run を正式結果として継ぎ足しません。
- Python の静的解析とテスト、Markdown の体裁とリンク確認を日常運用に含めます。
- 標準の観測・依存棚卸し用として `psutil`、`pipdeptree`、`deptry`、`snakeviz` を baseline に含めます。

shared agent canon は `vendor/agent-canon/` に committed snapshot として同梱します。将来的に upstream `agent-canon` repo を切っても、`git clone <template>` 直後の workspace だけで agent 関連の正本を参照できます。ownership と surface 種別は [SHARED_RUNTIME_SURFACES.md](/mnt/l/workspace/project_template/documents/SHARED_RUNTIME_SURFACES.md) を正本にし、`.github/workflows/agent-coordination.yml` は symlink ではなく vendor 正本から同期する root copy として扱います。

## まず読むもの

- `QUICK_START.md`
- `documents/README.md`
- `documents/linux-wsl-host-requirements.md`
- `documents/WORKFLOW_GUIDE.md`
- `documents/conventions/README.md`
- `documents/coding-conventions-python.md`
- 開発環境を触る場合は `docker/`
- host 前提を確認する場合は `documents/linux-wsl-host-requirements.md`
- 実験を行う場合は `documents/experiment-workflow.md`
- 実験 topic を作る場合は `experiments/README.md`
- topic registry を触る場合は `documents/experiment-registry.md`
- エージェントを使う場合は `agents/README.md`

## 日常の進め方

1. 何を変えるかを決めます。実装だけか、実験まで含むか、環境や文書更新が必要かを最初に切ります。
2. 変更前に `make ci-quick` を流して、Python と Markdown の基準が壊れていないことを確認します。
3. 実装、実験コード、文書、必要なら `docker/` を更新します。
4. 仕上げに `make ci` か必要な個別チェックを流します。
5. 長期に残す判断や実験知見は `notes/` に移し、正本ルールは `documents/` に反映します。

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

実験方法論そのものは `documents/experiment-workflow.md` と `documents/research-workflow.md` を正本にします。
agent に実験つき改造 loop を回させる場合は `agents/skills/experiment-change-loop.md` を入口にし、記録は `agents/templates/experiment_change_loop.md` を使います。
server で回す実験コードの実体テンプレは `experiments/_template/`、topic 正本は `experiments/registry.toml`、topic scaffold は `scripts/experiments/create_experiment_topic.py`、run metadata を残す入口は `scripts/experiments/run_managed_experiment.py` です。

## よく使うコマンド

```bash
make ci-quick
make ci
make docs-check
make experiment-check
make docker-build-check
python3 -m pyright
python3 -m pytest tests/ -q --tb=short
python3 -m ruff check python tests --select D,E,F,I,UP
pipdeptree --warn fail
deptry python
make tools-help
```

## Docker で Codex を使う

`docker/Dockerfile` には Codex CLI と `docker` CLI を同梱します。container runtime の正本は [docker/README.md](/mnt/l/workspace/project_template/docker/README.md) で、build / smoke は `docker/packs/*.toml` と `scripts/ci/run_container_pack.py` から実行します。コンテナに入ったあと、認証は各自の OpenAI アカウントで行います。対話認証は `codex login`、API key を使う場合は `printenv OPENAI_API_KEY | codex login --with-api-key` を使えます。

`docker/Dockerfile` か `docker/requirements.txt` を更新した変更では、`make docker-build-check` を通して build 可否を確認します。ローカルに `docker` / `podman` がない場合は、GitHub Actions の `Docker Build` workflow を使います。

repo-wide な tool 導入案は `agents/templates/environment_change_proposal.md` に理由、Docker 影響、validation、rollback を残します。

`safe.directory` は `docker/Dockerfile` の build 時に `git config --global` で固定します。template の canonical image では `/workspace` と、local bare remote 置き場として使う `/mnt/git/template.git`、`/mnt/git/agent-canon.git` を登録します。`/mnt/git` を mount した container からそのまま push/pull できる状態を先に作るためです。

VS Code の dev container は `.devcontainer/` から起動します。起動時に generated compose を 1 枚作り、GPU が見える host では `gpus: all` を自動追加し、GPU が無い host では CPU-only で起動します。`/mnt/git` も host に path がある場合だけ mount し、local bare remote への push/pull を container 内から継続できます。attach 直後には banner を出し、GPU、`/mnt/git`、Docker socket の状態を表示します。前提拡張は `.vscode/extensions.json` にまとめています。

container 内では `PYTHONPATH=/workspace/python` を前提にします。

```bash
docker build -t project-template -f docker/Dockerfile .
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v $(pwd):/workspace -w /workspace \
  project-template bash
codex --version
docker --version
codex login
```

container 内から `docker build` / `docker run` を行う場合は、上のように host の Docker socket を渡すか、別 daemon を用意します。

build 確認だけを行う場合は次です。

```bash
make docker-build-check
make docker-build-check-host-docker
make server-check
python3 scripts/ci/run_container_pack.py --pack docker/packs/default.toml --print-only
python3 scripts/ci/run_codex_in_repo_container.py --print-only
```

## 詳細入口

- 規約と運用: `documents/README.md`
- 補助メモ: `notes/README.md`
- エージェント運用: `agents/README.md`
- スクリプト一覧: `scripts/README.md`
