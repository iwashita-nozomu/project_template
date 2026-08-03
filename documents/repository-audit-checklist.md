<!--
@dependency-start
contract policy
responsibility Provides the parent-local reader route to the canonical parent repository audit.
upstream design ../vendor/agent-canon/documents/parent-repository-audit/README.md canonical audit reader route and unit boundary
upstream design ../vendor/agent-canon/documents/design/parent-repository-audit.md target state, migration, and failure semantics
upstream implementation ../vendor/agent-canon/tools/agent_tools/parent_repository_audit.py deterministic unit selection and coverage
upstream implementation ../vendor/agent-canon/agents/skills/parent-repository-audit.md public repair workflow
downstream design ../AGENTS.md parent runtime entrypoint and source-root resolver route
@dependency-end
-->

# Parent Repository Audit Reader Route

## Reader Map

- 正本を読む: [`AgentCanon Parent Repository Audit`](../vendor/agent-canon/documents/parent-repository-audit/README.md)
- 実行 skill を読む: [`parent-repository-audit`](../vendor/agent-canon/agents/skills/parent-repository-audit.md)
- unit を列挙する: source-root/path resolver 経由の `parent_repository_audit.py list`
- unit を検査する: 同じ resolver 経由の `parent_repository_audit.py check`
- 親固有の branch、commit、finding、修正、readback、defer は親側 evidence に記録する

このファイルは、既存の親側参照を壊さずに canonical audit surface へ到達するための
reader route です。監査 invariant、metadata、checkbox、command、owner repair route の
正本ではありません。

## Canonical Route

親 repository root から AgentCanon source root/path resolver を経由して、まず対象 unit を
決定論的に列挙し、その返却順に一つずつ読みます。

```bash
PYTHONPATH=vendor/agent-canon/tools:tools \
  python3 -m agent_tools.agent_canon_source_root exec \
  tools/agent_tools/parent_repository_audit.py list --root . --format text

PYTHONPATH=vendor/agent-canon/tools:tools \
  python3 -m agent_tools.agent_canon_source_root exec \
  tools/agent_tools/parent_repository_audit.py check --root . --format text
```

`README.md` と `audit-unit/*.md` の Markdown 集合だけが audit canon です。各 unit は
owner responsibility、invariant、evidence source、repair skill/tool、validation、close
condition、related change surface を自己完結して持ちます。各 unit を `pass`、または
`finding -> repair -> readback -> closed` まで終えてから次の unit に進みます。

## Legacy Checklist Migration

旧来のこのファイルに含まれていた metadata、checkbox、command は、AgentCanon の設計
packet にある stable item ID の一回限り migration ledger を経て対応する audit unit へ
移行済みです。ここへ旧項目を再掲せず、ledger を恒久的な第二 checklist にもしません。
未移行または意味が変わった項目を発見した場合は、関係する unit file だけを AgentCanon
側の同じ変更責務で更新します。

## Parent Evidence And Scope

この親側で保存するのは、対象 root の tracked-tree packet、source-root resolution、unit
ごとの pass または closure receipt、owner repair receipt、readback、blocked/defer receipt
です。generated summary、inventory、index、report は再生成可能な evidence/projection で
あり、canonical unit の代替にはしません。

static structure/readback で invariant が確定する unit では runtime build や全 suite を
追加しません。Docker image 間の差分 build、無関係な runtime log 修復、別 owner の clone
cleanup はこの projection の修正範囲に含めず、必要な場合は owner、理由、次の action を
具体的な defer receipt に残します。
