# Quick Start

このファイルは、テンプレート repo で作業を始めるための最短入口です。

## 1. 最初に読む

- [README.md](/mnt/l/workspace/project_template/README.md)
- [documents/README.md](/mnt/l/workspace/project_template/documents/README.md)
- [documents/WORKFLOW_GUIDE.md](/mnt/l/workspace/project_template/documents/WORKFLOW_GUIDE.md)
- [documents/linux-wsl-host-requirements.md](/mnt/l/workspace/project_template/documents/linux-wsl-host-requirements.md)
- [documents/template-bootstrap.md](/mnt/l/workspace/project_template/documents/template-bootstrap.md)
- [documents/conventions/README.md](/mnt/l/workspace/project_template/documents/conventions/README.md)
- [documents/coding-conventions-python.md](/mnt/l/workspace/project_template/documents/coding-conventions-python.md)

実験を扱う場合は追加で次を見ます。

- [documents/experiment-workflow.md](/mnt/l/workspace/project_template/documents/experiment-workflow.md)
- [documents/research-workflow.md](/mnt/l/workspace/project_template/documents/research-workflow.md)
- [documents/experiment-registry.md](/mnt/l/workspace/project_template/documents/experiment-registry.md)
- [experiments/README.md](/mnt/l/workspace/project_template/experiments/README.md)

agent を使う場合は次を見ます。

- [agents/README.md](/mnt/l/workspace/project_template/agents/README.md)
- [documents/AGENTS_COORDINATION.md](/mnt/l/workspace/project_template/documents/AGENTS_COORDINATION.md)

## 2. 作業の始め方

- 既定の統合先は `main` です。
- 短期 branch は必要なときだけ切り、長期の分岐運用は避けます。
- branch 側で file 構成を変えた場合は、`documents/main-integration-workflow.md` を見て integration worktree で戻します。
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

- `documents/conventions/README.md` と `documents/coding-conventions-python.md` を先に見ます。
- agent workflow を使う変更なら `documents/WORKFLOW_GUIDE.md` と `agents/canonical/CODEX_WORKFLOW.md` を確認します。

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
bash scripts/run_comprehensive_review.sh
```

## 5. 実験の基本

- 実験コードは `experiments/<topic>/` に置きます。
- topic の正本 entrypoint と formal command は `experiments/registry.toml` に置きます。
- 新しい topic は `python3 scripts/experiments/create_experiment_topic.py <topic>` で作ります。
- 実行ごとの生成物は `experiments/<topic>/result/<run_name>/` に置きます。
- 1 回の実験 report は `experiments/report/<run_name>.md` に置きます。
- server で formal run を回すときは `scripts/experiments/run_managed_experiment.py --topic <topic> --use-registered-command formal` で `run_manifest.json` と `run.log` を残します。
- partial run を正式結果として扱いません。
- agent に実験つき改造 loop を回させる場合は `agents/skills/experiment-change-loop.md` と `agents/templates/experiment_change_loop.md` を使います。

## 6. 環境の基本

- 共通開発環境は `docker/` を基準にします。
- host 前提は `documents/linux-wsl-host-requirements.md` を正本にします。
- container runtime の再利用 surface は `docker/packs/*.toml` と `scripts/ci/run_container_pack.py` を基準にします。
- Python 依存を追加する場合は `docker/Dockerfile` と `docker/requirements.txt` を同時に更新します。
- `docker/Dockerfile` か `docker/requirements.txt` を更新したら `make docker-build-check` を流します。
- repo-wide な tool 導入案や Docker 変更では `agents/templates/environment_change_proposal.md` に triggering code requirement と blocked command を先に記録します。
- container 内では `PYTHONPATH=/workspace/python` を前提にします。
- Markdown の体裁ルールは `.markdownlint.json` と `documents/conventions/common/05_docs.md` を基準にします。
- 依存棚卸しは `pipdeptree` と `deptry` を baseline にします。

Codex CLI と `docker` CLI は `docker/Dockerfile` に同梱します。コンテナ内では `codex login`、API key を使う場合は `printenv OPENAI_API_KEY | codex login --with-api-key` を使います。`safe.directory` は image build 時に `git config --global` で固定し、既定で `/workspace` と local bare remote 用の `/mnt/git/template.git`、`/mnt/git/agent-canon.git` を登録します。project-scoped Codex config の `.codex/config.toml` では `approval_policy = "never"` と `sandbox_mode = "danger-full-access"` を既定にしているので、container 内で起動した Codex も最初から full access です。

VS Code から開発コンテナへ入る場合は `.devcontainer/` を使います。起動時に generated compose を 1 枚作り、GPU がある host では自動で `gpus: all` を追加し、GPU が無い host では CPU-only で起動します。`/mnt/git` も host に存在するときだけ mount し、container 内から local bare remote へ push/pull できます。attach 直後には banner を出し、GPU、`/mnt/git`、Docker socket、Codex の `approval_policy` / `sandbox_mode` を表示します。前提拡張は `.vscode/extensions.json` を見ます。

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

build 可否だけを確認したい場合は次です。

```bash
make docker-build-check
make docker-build-check-host-docker
make server-check
python3 scripts/ci/run_container_pack.py --pack docker/packs/default.toml --print-only
python3 scripts/ci/run_codex_in_repo_container.py --print-only
```

## 7. 終了時の整理

```bash
git status --short
git branch --show-current
bash scripts/push_origin.sh
```

- 長期に残す知見は `notes/` に寄せます。
- worktree を使った場合は、`documents/notes-lifecycle.md` を見て action log から knowledge/theme/failure へ昇格させる項目を決めます。
- repo 全体のルール変更は `documents/` に反映します。
- 短期 branch を使った場合は、統合後に削除して `main` に戻します。
