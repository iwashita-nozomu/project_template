# コーディング規約（共通）

この文書は、general なコーディング方針の全体像を短くまとめる文書です。
共通ルールの詳細は各章に分けますが、この文書自体も概要が読めるように保ちます。

## 共通規約（章ごとの要約）

1. [基本方針](./conventions/common/01_principles.md) — 読みやすさ・保守性・依存最小を最優先にします。
1. [命名](./conventions/common/02_naming.md) — 役割が伝わる名前を使い、省略を最小限にします。
1. [コメント](./conventions/common/03_comments.md) — 意図と前提を明確にし、数式や安定性の注意を優先します。
1. [演算子記法（共通）](./conventions/common/04_operators.md) — 適用は `@`、合成は `*` を基本にします。
1. [ドキュメント運用](./conventions/common/05_docs.md) — 実装変更に合わせて文書も更新し、禁止事項は `禁止` と明記します。

## Markdown 書式修正ルール

**必須ルール: md ファイル編集後は必ず `mdformat` ツールで書式を直してください。**

### Canonical Only

- `documents/`、`tools/`、`scripts/` の Markdown には正本だけを残します。
- `.bak`、proposal、report、summary のような履歴用ファイルを常設しません。
- 履歴を残したい場合は Git 履歴を使い、必要な内容だけを既存の正本へ統合します。

### 実行方法

```bash
# 単一ファイル編集後
mdformat path/to/file.md

# 複数ファイル一括修正
mdformat path/to/docs/ tools/ scripts/

# 修正前に確認（ドライラン）
mdformat --check path/to/file.md
```

## 対象ファイル

- `documents/` 配下の全 `.md` ファイル
- `tools/` 配下の全 `.md` ファイル
- `scripts/` 配下の全 `.md` ファイル
- `.github/` 配下の全 `.md` ファイル
- `README.md` や各種運用ドキュメント

### ツール設定

`mdformat` は以下の拡張を有効にしています：

- `mdformat-gfm`: GitHub Flavored Markdown 対応
- `mdformat-myst`: MyST 対応
- `mdformat-front-matters`: YAML front matter 対応

### CI 統合

Markdown 整形とリンク監査は `mdformat` に加えて `make docs-check` で確認します。
`make ci`、`make ci-quick`、`tools/ci/run_all_checks.sh` は同じ文書チェックを呼び出します。

## Bash 実装の置き場所

- shared automation の Bash 実装は `tools/` に置かなければなりません。
- repo-local bootstrap の Bash 実装は `scripts/` に置かなければなりません。
- agent helper、CI、review、validation、container runner、experiment helper の Bash を `scripts/` に置くことを禁止します。

## Python 実装向けの追加規約

- [ハウススタイル規約](./coding-conventions-house-style.md)
- [Python 規約](./coding-conventions-python.md)
- [テスト規約](./coding-conventions-testing.md)
- [ログ規約](./coding-conventions-logging.md)
- [プロジェクト運用規約](./coding-conventions-project.md)
