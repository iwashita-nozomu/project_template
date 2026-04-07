# Quick Start

このファイルは、テンプレート repo で作業を始めるための最短入口です。

## 1. 最初に読む

- [README.md](/mnt/l/workspace/project_template/README.md)
- [documents/README.md](/mnt/l/workspace/project_template/documents/README.md)
- [documents/WORKFLOW_GUIDE.md](/mnt/l/workspace/project_template/documents/WORKFLOW_GUIDE.md)
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
- 変更の前に、対象ディレクトリと必要な更新を先に決めます。
- Python と Markdown は常に対象に含まれる前提で確認します。

最低限の確認:

```bash
git status --short
make ci-quick
python3 -m pyright
```

## 3. 実装前の確認

```bash
bash scripts/guide.sh
bash scripts/view_conventions.sh
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
- container runtime の再利用 surface は `docker/packs/*.toml` と `scripts/ci/run_container_pack.py` を基準にします。
- Python 依存を追加する場合は `docker/Dockerfile` と `docker/requirements.txt` を同時に更新します。
- `docker/Dockerfile` か `docker/requirements.txt` を更新したら `make docker-build-check` を流します。
- repo-wide な tool 導入案は `agents/templates/environment_change_proposal.md` に記録します。
- container 内では `PYTHONPATH=/workspace/python` を前提にします。
- Markdown の体裁ルールは `.markdownlint.json` と `documents/conventions/common/05_docs.md` を基準にします。
- 依存棚卸しは `pipdeptree` と `deptry` を baseline にします。

Codex CLI と `docker` CLI は `docker/Dockerfile` に同梱します。コンテナ内では `codex login`、API key を使う場合は `printenv OPENAI_API_KEY | codex login --with-api-key` を使います。`safe.directory` は起動時に現在の working directory を自動登録し、追加 path は `GIT_SAFE_DIRECTORIES` で渡します。

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
```

- 長期に残す知見は `notes/` に寄せます。
- repo 全体のルール変更は `documents/` に反映します。
- 短期 branch を使った場合は、統合後に削除して `main` に戻します。
