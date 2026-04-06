# 実装者向けワークフローガイド

この文書は、Python 実装、テスト、文書同期を担当する利用者向けの入口です。
repo 全体の見取り図は `documents/WORKFLOW_GUIDE.md` を見てください。

## 最初にやること

1. どの実装を変えるか
1. どのテストが影響を受けるか
1. どの正本文書を同時に直すか

```bash
git status --short
make ci-quick
python3 -m pyright
```

## 主に触る場所

- 実装:
  - `python/`
- テスト:
  - `python/tests/`
- 規約:
  - `documents/coding-conventions-python.md`
- プロジェクト全体ルール:
  - `documents/coding-conventions-project.md`
- スクリプト:
  - `scripts/`

## 標準フロー

1. 実装対象と関連テストを決める
1. 変更前に baseline を確認する
1. 実装と文書を同じ変更で直す
1. 早い確認を回す
1. 仕上げ前に full check を回す

```bash
python3 -m pytest python/tests/ -q --tb=short
python3 -m pyright
python3 -m ruff check python/ --select D,E,F,I,UP
make ci
```

## 文書も同時に直すとき

実装だけで意味が変わる変更は incomplete 扱いです。少なくとも次のどれかは確認します。

- `documents/`
- `README.md`
- `QUICK_START.md`
- `scripts/README.md`
- `docker/README.md`

```bash
make docs-check
python3 scripts/tools/check_markdown_lint.py --check <changed-file>.md
```

## Docker や依存も触るとき

依存や runtime に触る場合は、実装者でも `docker/` が正本です。

```bash
python3 scripts/docker_dependency_validator.py
make docker-build-check
python3 scripts/ci/run_python_in_dockerfile.py docker/Dockerfile scripts/docker_dependency_validator.py --print-only
```

## close 条件

- `make ci-quick` が通る
- 必要なら `make ci` が通る
- 関連文書が更新されている
- 不要な scratch file を残していない
- commit と push が完了している
