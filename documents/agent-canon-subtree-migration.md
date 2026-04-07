# agent-canon subtree 移行計画

この文書は、shared agent canon を別 repo `agent-canon` として切り出し、product template 側へ `git subtree` で取り込むための正本です。
目的は、`git clone <template>` だけで新しい product を始められることを維持しながら、agent 運用の正本を upstream repo へ分離することです。

## 1. この構成を選ぶ理由

- `git clone <template>` だけで product を開始したい
- product 側の worktree に、その時点の agent canon snapshot を閉じ込めたい
- product 側で直した shared canon を、後から upstream `agent-canon` repo へ戻したい
- Codex の runtime discovery は root `AGENTS.md` と root `.codex/` を前提にしたい
- sibling repo 参照や手動コピーには依存したくない

この条件では、`submodule` より `subtree` の方が扱いやすく、repo 外参照より再現性が高いです。

## 2. 非目標

- `agent-canon` を repo 外の sibling directory として自動 discovery させること
- root `AGENTS.md` と root `.codex/` を無くすこと
- branch を product variant ごとに長期運用すること
- 一回の変更で template から agent 関連を全部剥がすこと

## 3. 目標構成

```text
product-repo/
├─ AGENTS.md
├─ CLAUDE.md
├─ .github/copilot-instructions.md
├─ .codex/
│  ├─ config.toml
│  └─ README.md
├─ vendor/
│  └─ agent-canon/
│     ├─ agents/
│     ├─ .agents/
│     ├─ .claude/
│     ├─ .codex/agents/
│     └─ shared agent-facing docs
├─ python/
├─ docker/
├─ documents/
└─ scripts/
```

原則:
- root `AGENTS.md` と root `.codex/` は product repo の runtime entrypoint として残します
- shared canon の実体は `vendor/agent-canon/` の subtree snapshot に寄せます
- product 固有の README、Docker、CI、実装、server 運用文書は root 側に残します

## 4. 所有境界

### 4.1 `agent-canon` へ移すもの

phase 1 で移す対象:
- `agents/`
- `.agents/skills/`
- `.claude/skills/`
- `.codex/agents/`
- `agents/templates/`

phase 2 で移す候補:
- `documents/AGENTS_COORDINATION.md`
- `documents/REVIEW_PROCESS.md`
- `documents/implementation-waterfall-workflow.md`
- `documents/workflow-references.md`

phase 2 を後ろにずらす理由:
- これらの文書は link と root path の参照がまだ強い
- product 固有の Docker / server / experiment 文書との導線が密結合している

### 4.2 product template に残すもの

- root `AGENTS.md`
- root `CLAUDE.md`
- root `.github/copilot-instructions.md`
- root `.codex/config.toml`
- root `.codex/README.md`
- `README.md`
- `docker/`
- `scripts/`
- `python/`
- `documents/` のうち product / environment / server / experiment に閉じるもの

### 4.3 vendor-aware 化が必要な support surface

shared canon を subtree 化すると、次の script は `vendor/agent-canon/` を見られるように直す必要があります。

- `scripts/tools/mirror_skill_shims.py`
- `scripts/agent_tools/bootstrap_agent_run.py`
- `scripts/agent_tools/smoke_test_research_perspective_pack.py`
- `scripts/agent_tools/validate_role_write_scope.py`
- `scripts/agent_tools/agent_team.py`

この移行では、これらを即座に動かし替えるのではなく、まず subtree 運用の入口を追加し、次の pass で vendor-aware 化します。

## 5. wrapper の考え方

root 側は次のような薄い wrapper にします。

- `AGENTS.md`
  - Codex / Copilot の root entrypoint
  - `vendor/agent-canon/` 内の正本への導線だけを持つ
- `.codex/README.md`
  - project-scoped Codex runtime の入口
  - model policy や subagent inventory の正本を `vendor/agent-canon/` へ向ける
- `CLAUDE.md`
  - shared canon を参照する adapter に限定する
- `.github/copilot-instructions.md`
  - Copilot 固有差分だけに限定する

重要:
- subtree 配下にも `AGENTS.md` は置けますが、通常は canon 開発 subtree 用 override としてのみ使います
- product runtime の正面入口は root に固定します

## 6. worktree と subtree の関係

- product repo で worktree を切ると、その branch / commit に入っている `vendor/agent-canon/` snapshot がそのまま見えます
- upstream `agent-canon` の最新が自動で流入するわけではありません
- shared canon の更新は、明示的に subtree pull した branch にだけ反映されます

つまり:
- worktree は snapshot を使う仕組み
- shared canon 更新は subtree sync で行う仕組み

## 7. 標準運用

### 7.1 初回取り込み

```bash
bash scripts/sync_agent_canon.sh add git@github.com:<org>/agent-canon.git
```

### 7.2 upstream から更新取得

```bash
bash scripts/sync_agent_canon.sh pull
```

### 7.3 product 側の shared canon 変更を upstream へ戻す

```bash
bash scripts/sync_agent_canon.sh push
```

### 7.4 現在の設定確認

```bash
bash scripts/sync_agent_canon.sh status
```

## 8. 移行フェーズ

### Phase 0. この変更で入れる土台

- migration 正本を作る
- `vendor/` の reserved path を作る
- subtree sync script を追加する
- index 文書に導線を足す

### Phase 1. upstream `agent-canon` repo を作る

- `agents/`
- `.agents/skills/`
- `.claude/skills/`
- `.codex/agents/`
- `agents/templates/`

を upstream repo へ移す

exit 条件:
- upstream repo 単体で shared canon を保持できる
- product 側に subtree add 済み snapshot を持てる

### Phase 2. template の runtime entrypoint を薄くする

- root `AGENTS.md`
- root `.codex/README.md`
- `CLAUDE.md`
- `.github/copilot-instructions.md`

を vendor 参照の wrapper へ薄化する

exit 条件:
- Codex discovery は root で完結する
- shared canon の正本は subtree 側だけになる

### Phase 3. support script を vendor-aware 化する

対象:
- mirror
- bootstrap
- smoke test
- role write scope
- agent team runtime

exit 条件:
- `make agent-checks` が `vendor/agent-canon/` 前提で通る
- root 側 wrapper と vendor 側 canon の参照が一致する

### Phase 4. product bootstrap command を追加する

候補:
- `scripts/bootstrap_product.py`
- `scripts/new_product.sh`

役割:
- template clone 後の product 名差し替え
- subtree remote 設定
- optional pack 選択

## 9. リスクと抑止策

### root entrypoint が壊れる

抑止:
- root `AGENTS.md` と root `.codex/` は最後まで消さない
- subtree 化前に wrapper へ薄化しない

### shared canon と product 固有文書が混ざる

抑止:
- `agent-canon` へ移す範囲を phase で分ける
- Docker、server、experiment の文書は product 側に残す

### product 側で直した canon を upstream へ戻せない

抑止:
- `vendor/agent-canon/` の変更は専用 commit に分ける
- `git subtree push --prefix=vendor/agent-canon` を標準運用にする

### worktree ごとに shared canon がばらつく

抑止:
- それは意図した snapshot 運用とみなす
- どの branch がどの subtree commit を含むかを commit history で追えるようにする

## 10. 完了条件

- upstream `agent-canon` repo が存在する
- template repo が `vendor/agent-canon/` subtree snapshot を持つ
- root `AGENTS.md` と root `.codex/` は product entrypoint として機能する
- product で worktree を切ったとき、その時点の shared canon snapshot が `vendor/agent-canon/` として見える
- product 側で直した shared canon を `git subtree push` で upstream へ戻せる

## 11. 関連

- [README.md](/mnt/l/workspace/project_template/README.md)
- [AGENTS.md](/mnt/l/workspace/project_template/AGENTS.md)
- [WORKFLOW_GUIDE.md](/mnt/l/workspace/project_template/documents/WORKFLOW_GUIDE.md)
- [workflow-references.md](/mnt/l/workspace/project_template/documents/workflow-references.md)
- [README.md](/mnt/l/workspace/project_template/vendor/README.md)
- [sync_agent_canon.sh](/mnt/l/workspace/project_template/scripts/sync_agent_canon.sh)
