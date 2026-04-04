# Skill 実装ガイド

この文書は、repo で使う project skill の実装指針です。
現在の正本は `agents/` と discovery path の skill directory です。

## 正本

- 人間向けハブ: `agents/README.md`
- canonical layout: `agents/canonical/README.md`
- skill registry: `agents/canonical/skills.md`
- artifact placement canon: `agents/canonical/ARTIFACT_PLACEMENT.md`
- CLI entrypoint canon: `agents/canonical/CLI_ENTRYPOINTS.md`
- Codex / Copilot discovery path: `.agents/skills/`
- Claude compatibility path: `.claude/skills/`

## 方針

- skill は少数の workflow-oriented unit に保ちます。
- numbered skill catalog は増やしません。
- skill ごとの instructions は `SKILL.md` に集約します。
- 再利用可能な workflow は skill にし、repo 全体の恒久ルールは `documents/` または `agents/` に置きます。

## 推奨 skill directory

```text
<skill-name>/
└── SKILL.md
```

必要な場合だけ次を追加します。

```text
<skill-name>/
├── SKILL.md
├── scripts/
├── references/
└── assets/
```

## 書き方

- `name` と `description` を frontmatter に入れます。
- `description` には、いつ使うかと使わないかを明確に書きます。
- `SKILL.md` では、実行手順より判断手順を優先します。
- skill 内で repo 正本を再定義しません。必要な文書へリンクします。

## 整理ルール

- 新しい skill を追加するときは `agents/canonical/skills.md` を更新します。
- Claude mirror が必要なら `.claude/skills/` に対応 skill を追加します。
- 古い agent-specific skill artifacts は `agents/legacy/` に退避します。
