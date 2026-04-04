# Quick Start

このファイルは、テンプレート repo で作業を始めるための最短入口です。

## 1. 最初に読む

- [README.md](/mnt/l/workspace/project_template/README.md)
- [documents/README.md](/mnt/l/workspace/project_template/documents/README.md)
- [documents/conventions/README.md](/mnt/l/workspace/project_template/documents/conventions/README.md)
- [documents/coding-conventions-python.md](/mnt/l/workspace/project_template/documents/coding-conventions-python.md)

実験を扱う場合は追加で次を見ます。

- [documents/experiment-workflow.md](/mnt/l/workspace/project_template/documents/experiment-workflow.md)
- [documents/research-workflow.md](/mnt/l/workspace/project_template/documents/research-workflow.md)

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
python3 -m pyright python/
```

## 3. 実装前の確認

```bash
bash scripts/guide.sh
bash scripts/view_conventions.sh
make ci-quick
python3 -m pytest python/tests/ -q --tb=short
pipdeptree --warn fail
python3 scripts/tools/check_markdown_lint.py documents
```

フルチェック:

```bash
make ci
```

## 4. よく使うコマンド

```bash
make ci-quick
make ci
bash scripts/run_comprehensive_review.sh
python3 scripts/tools/check_markdown_lint.py documents
python3 scripts/tools/audit_and_fix_links.py documents
```

## 5. 実験の基本

- 実験コードは `experiments/<topic>/` に置きます。
- 実行ごとの生成物は `experiments/<topic>/result/<run_name>/` に置きます。
- 1 回の実験 report は `experiments/report/<run_name>.md` に置きます。
- partial run を正式結果として扱いません。

## 6. 環境の基本

- 共通開発環境は `docker/` を基準にします。
- Python 依存を追加する場合は `docker/Dockerfile` と `docker/requirements.txt` を同時に更新します。
- Markdown の体裁ルールは `.markdownlint.json` と `documents/conventions/common/05_docs.md` を基準にします。
- 依存棚卸しは `pipdeptree` と `deptry` を baseline にします。

## 7. 終了時の整理

```bash
git status --short
git branch --show-current
```

- 長期に残す知見は `notes/` に寄せます。
- repo 全体のルール変更は `documents/` に反映します。
- 短期 branch を使った場合は、統合後に削除して `main` に戻します。
