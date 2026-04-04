日本語で対応してください。
複雑な分岐は避け、シンプルで追いやすい実装を優先してください。

# GitHub Copilot Instructions

## 基本方針

- repo 全体の入口は言語非限定です。
- 既定の統合先は `main` です。
- 長期に残すルールは `documents/`、補助知見は `notes/` に置きます。
- agent の使い方や workflow は `agents/` と `documents/AGENTS_COORDINATION.md` を参照します。

## 規約

- `documents/` の規約に従ってください。
- 最初に `documents/coding-conventions-project.md` を確認してください。
- 言語固有の補足は、その言語を触るときだけ参照してください。

## 開発環境

- 共通開発環境は `docker/` を基準にします。
- Python を使う場合は `docker/Dockerfile` と `docker/requirements.txt` を依存の正本にします。
- 環境更新時は関連 README や運用文書も同じ変更で更新してください。

## ドキュメント

- Markdown の入口リンクを壊さないでください。
- 実験手法やワークフローの一般論は残し、個別プロジェクト固有の記録は混ぜないでください。
