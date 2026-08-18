<!--
@dependency-start
contract design
responsibility Defines the template-maintainer-only transaction that imports one reviewed AgentCanon static-seed export into the tracked consumer snapshot.
upstream design ../contracts/template-bootstrap.md descendant bootstrap must not mutate the static seed
upstream design ../../README.md source-free template and maintainer boundary
upstream implementation ../../tools/check_runtime_independence.py post-import consumer-side closure check
upstream reference AgentCanon #716 at c5fa3a22c8486952dc6dede0cc3a25e5ba7741e5 static exporter and consumer-static semantic closure
downstream implementation ../../tools/import_agent_canon_static_seed.py one-way maintainer importer
downstream design ../contracts/template-bootstrap.md descendant no-refresh boundary
@dependency-end
-->

# Template Static-Seed Import Transaction

## 責務と境界

`project_template` が所有する static seed の更新入口は
`tools/import_agent_canon_static_seed.py` 一つです。この command は、AgentCanon producer が
生成し、template maintainer がレビュー対象として選んだ export directory を、template の
tracked snapshot へ一方向に取り込みます。

```bash
python3 tools/import_agent_canon_static_seed.py \
  --bundle <fresh-export-directory>
```

この入口は template 保守専用です。`Makefile` の通常 target、pytest の標準収集、bootstrap、
fresh-clone acceptance、GitHub Actions、Docker、Dev Container、生成後の派生 repository から
呼び出しません。派生 repository は取り込み済み regular file を読む consumer であり、
AgentCanon source、checkout、submodule、runtime dispatcher、network、credential、latest 判定、
同期状態を所有しません。

## 入力 authority

bundle の許可 path は次の exact closure だけです。

```text
agent-canon-static-seed.json
.codex/config.toml
.codex/agents/<role>.toml
```

全 file は regular file、mode `0644`、link count 1 でなければなりません。symlink、hard link、
実行可能 file、nested directory、未参照 role、欠落 role、unexpected entry は mutation 前に
拒否します。`.codex/config.toml` の role 登録と `.codex/agents/<same-role>.toml` は完全一致させ、
provenance は次の key だけを持ちます。

```json
{
  "schema_version": 1,
  "source_commit": "<lowercase 40-or-64-hex object id>",
  "source_repository": "iwashita-nozomu/agent-canon"
}
```

受理する payload bytes は importer 内の `REVIEWED_SOURCE_COMMIT` と
`REVIEWED_PAYLOAD_MANIFEST` に固定します。任意の future export を prose や pattern の類似だけで
受理せず、maintainer review で manifest を更新した change だけを新しい authority とします。
`tests/fixtures/static-seed-c5fa3a22/` は、この reviewed payload の repository 内参照資料として
残しますが、通常の template test suite が AgentCanon importer の内部状態機械を所有する根拠には
しません。

入力 bytes は producer-only path、live runtime、updater、network、secret、source checkout を
示す marker を含めません。検査は危険 surface を明確な typed finding で拒否するための境界であり、
free-prose の意味同値を推論する validator ではありません。

## Controlled write set

成功時に変更してよい tracked path は次だけです。

```text
agent-canon-static-seed.json
.codex/config.toml
.codex/agents/*.toml
```

新規 role、既存 role の更新、upstream で削除された stale role の削除は一つの deterministic plan
で扱います。bundle、repository metadata、隣接 file、bootstrap source、CI、Docker、文書を importer
が変更してはなりません。同一 bundle の再適用は temporary journal も作らない no-op です。

## Transaction invariant

multi-file 更新の安全性は、各 file の rename が単独で atomic であることだけには依存しません。
次の順序と証拠を一つの transaction invariant とします。

1. bundle 全体、provenance、config-role closure、mode、type、reviewed digest を読み切り、mutation
   前に immutable plan を作る。
2. `.codex/agents` directory descriptor に nonblocking exclusive lock を取得し、同時 importer は
   `TSSI_CONCURRENT_IMPORT` で直ちに拒否する。
3. target の path、bytes、mode、device、inode を lock 下で snapshot し、bundle と target の
   descriptor identity を apply 直前まで再検証する。
4. target と同じ filesystem の private journal に new bytes と complete backup を durable 化し、
   `COMPLETE`、`rollback-required`、manifest state を定めた順序で fsync する。
5. controlled path だけを deterministic order で replace または delete する。
6. live target を再読込し、path set、bytes、mode、source commit、role closure、reviewed digest を
  確認した後にだけ `committed` evidence を durable 化する。
7. apply または readback が失敗した場合は complete backup を逆順 replay し、pre-import の path、
   bytes、mode を完全に復元できたことを確認してから failure を返す。

prevalidation failure は target を一切変更しません。journal の schema、closure、marker、state が
不明または矛盾する場合は推測して cleanup や apply を継続せず、journal を保持して fail-closed に
します。process kill や power loss 後も、次回 invocation は新しい plan より先に既存 journal を
検証し、未commit状態は rollback、commit済み状態は candidate readback後のcleanupだけを行います。

## Stable result contract

通常成功と no-op は一行の機械可読 output を返します。

```text
TEMPLATE_STATIC_SEED_IMPORT=pass source_commit=<id> roles=<n> added=<n> updated=<n> deleted=<n>
TEMPLATE_STATIC_SEED_IMPORT=noop source_commit=<id> roles=<n> added=0 updated=0 deleted=0
```

failure は `TSSI_*` finding と非zero exitで表し、partial success や warning-only completion を
許しません。branch、timestamp、latest、sync history は result と provenance に追加しません。

## Consumer verification ownership

通常の template test suite が所有するのは、取り込み transaction の内部状態機械ではなく、
取り込み後の consumer tree が自己完結していることです。

- `tools/check_runtime_independence.py` は static seed の regular-file shape、provenance、role closure、
  live AgentCanon runtime の再流入を検査する。
- AgentCanon producer は exporter と consumer-static projection の closure を producer 側で検査する。
- template の `tests/tools` には AgentCanon importer 専用の executable test module、別名 wrapper、
  skip-only module、dispatcher を置かない。
- importer の実装、static seed、reviewed fixtureを通常の派生 repository lifecycleへ接続しない。

この分離により、producer、maintainer transition、consumer の三責務を混在させず、通常の
`make test` は project template 自身が所有する契約だけを収集します。

## Invariants

- `TSSI-001`: maintainer command は bundle directory 以外の source、remote、network、secret、
  latest、sync inputを持たない。
- `TSSI-002`: bundle は reviewed manifest、provenance、regular-file mode、same-role closureに完全一致する。
- `TSSI-003`: source/runtime/updater/network/credential surfaceはtarget mutation前に拒否する。
- `TSSI-004`: write setはprovenance、config、direct role filesだけに閉じる。
- `TSSI-005`: prevalidation failureとno-opはtarget mutationを行わない。
- `TSSI-006`: non-empty planはdurable stage、complete backup、exclusive lock、restart recoveryを使う。
- `TSSI-007`: successはlive targetのexact readbackとcommit evidenceより後にだけ返す。
- `TSSI-008`: rollbackはpre-import path、bytes、modeの完全復元をsuccess条件とする。
- `TSSI-009`: bootstrap、CI、Docker、fresh clone、通常pytestはimporterを実行・要求しない。
- `TSSI-010`: unknownまたはmalformed recovery evidenceは保持し、推測でcommit・rollback・cleanupしない。

## Validation route

この設計または importer ownership を変更する template change は、通常の project gate と
source-free descendant acceptance で検証します。

```bash
make pr-check
make fresh-clone-check
git diff --check
```

レビューでは追加で、削除済み AgentCanon importer test path が tracked tree と
`documents/design/template-static-seed-import.md` の必須 gate 記述へ戻っていないこと、importer、
static seed、reviewed fixture、runtime-independence checkerに意図しない差分がないことを確認します。
