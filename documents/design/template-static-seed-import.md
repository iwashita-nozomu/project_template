<!--
@dependency-start
contract design
responsibility Defines the template-maintainer-only transaction that imports one fresh AgentCanon static-seed export into the tracked consumer snapshot.
upstream design ../contracts/template-bootstrap.md descendant bootstrap must not mutate the static seed
upstream design ../../README.md source-free template and maintainer boundary
upstream implementation ../../tools/check_runtime_independence.py post-import consumer-side closure check
upstream reference AgentCanon #716 at c5fa3a22c8486952dc6dede0cc3a25e5ba7741e5 static exporter and consumer-static semantic closure
downstream implementation ../../tools/import_agent_canon_static_seed.py planned one-way importer
downstream implementation ../../tests/tools/test_import_agent_canon_static_seed.py planned transaction and rollback tests
downstream design ../contracts/template-bootstrap.md planned command/documentation readback
@dependency-end
-->

# Template Static-Seed Import Transaction

## 責務と根本原因

Issue #169 の責務は、AgentCanon が生成した **一つの fresh export directory** を、
この template が所有する tracked static snapshot へ一方向に取り込む template-maintainer
入口を一つ定義することです。PR #168 の現状態には consumer-side の
`tools/check_runtime_independence.py` しかなく、export bundle を検証して config、role の
追加・更新・削除、provenance を一つの操作として反映する owner がありません。そのため
「explicit import」が複数ファイルの手作業 copy/delete に退行しています。

この文書は importer の canonical design owner です。AgentCanon の exporter、registry、
checkout、source resolver、network、updater は consumer の実装依存ではありません。AgentCanon
#716 が確定した static export contract（merge commit
`c5fa3a22c8486952dc6dede0cc3a25e5ba7741e5`）を入力の意味として再利用し、template 側は
その出力を検証して exact bytes を所有 tree へ移します。

## Owner、replaceable unit、API

責務 owner は template root の `tools/import_agent_canon_static_seed.py` 一つです。
この file が bundle validation、plan、apply、readback、rollback、stable result line を
所有します。別の validator、updater、dispatcher、role ごとの wrapper、source-side tool の
copy は追加しません。

公開する command は次の一つだけです。

```bash
python3 tools/import_agent_canon_static_seed.py \
  --bundle <fresh-export-directory>
```

`--bundle` は AgentCanon `export_static_seed.py` が作成したと template maintainer が確認した
既存 directory だけを受け取ります。この freshness は importer が時刻や source checkout
から証明する性質ではなく、maintainer の trust-boundary です。importer が観測できる証拠は
exact closure、regular file、mode、provenance、semantic prefix closure だけです。command の
引数には source root、commit/ref、remote、branch、latest、URL、token、secret、checkout path、sync state を含めません。importer は標準 Python と
filesystem の read/write だけを使い、Git、AgentCanon checkout、network、環境変数からの
credential、producer module import を読みません。

target root は arbitrary current working directory に依存しません。実装は
`Path(__file__).resolve(strict=True).parents[1]` から project root を一度解決し、その root の
`.codex` / `.codex/agents` shape を検証します。`--bundle` の raw argument は lexical string
として保持し、`Path.resolve()` で symlink を追って canonicalize しません。相対 argument は
caller cwd と lexical に結合し、absolute argument もその lexical spelling を保ったまま、
parent directory fd を component ごと `O_DIRECTORY|O_NOFOLLOW` で開きます。最後の component
は `lstat(..., AT_SYMLINK_NOFOLLOW)` で先に通常 directory と確認してから、parent fd に対する
`openat(..., O_DIRECTORY|O_NOFOLLOW)` を実行し、open 後の fd `fstat` の device/inode を唯一の
bundle identity とします。lstat と openat の間の root symlink swap は reject します。

root の `Makefile` にはこの command を呼ぶ maintainer target を追加しません。通常の
bootstrap、fresh-clone check、CI、Docker、container 起動、`scripts/start_repository.sh`
から呼び出されないことを実装とテストで固定します。保守者は command を明示的に実行し、
同じ change で provenance と diff を review・commit します。これは generated repository
へ伝播する runtime surface ではありません。

## Controlled snapshot と side-effect 境界

成功時に bytes、mode、path が変化してよい file は次の集合だけです。

```text
agent-canon-static-seed.json
.codex/config.toml
.codex/agents/<role>.toml
```

`<role>` は config の同名 role から導出する一段の basename です。`.codex` と
`.codex/agents` は既存の通常 directory でなければならず、directory 自体の mode、隣接
file、repository metadata は変更しません。新しい role は create、既存 role は replace、
入力にない既存の direct `*.toml` role は stale として delete します。directory 内の
symlink、nested directory、非 TOML file、または control path の symlink は stale として
消さず、target-shape failure にします。これにより importer の destructive write set は
明示した三つの file surface に閉じます。

bundle は読取り専用です。bundle 内の file、source checkout、remote、作業 tree の上記外側
path は変更しません。import の副作用は template maintainer が明示した時の controlled
snapshot write だけであり、descendant user、bootstrap、CI、runtime の副作用ではありません。

## Bundle の exact closure

mutation 前に bundle 全体を `lstat` で走査し、次の exact path set 以外を拒否します。

```text
agent-canon-static-seed.json
.codex/config.toml
.codex/agents/<role>.toml  (config が参照する role ごとに一つ)
```

受理する directory は bundle root、`.codex`、`.codex/agents` だけです。入力 root、各
directory、各 file は symlink ではなく通常 object であり、gitlink、FIFO、device、実行可能
file、regular file の `st_nlink != 1` hard-link、隠し temporary file、nested path、unreferenced role を
拒否します。正規 mode は全 file `0644` とし、入力に他の mode があれば mutation 前に失敗
します。path は UTF-8 の canonical relative POSIX path として扱い、empty、`.`、`..`、`\\`、
NUL、absolute path を拒否します。

`st_nlink == 1` の検査は regular file にだけ適用します。directory は `S_ISDIR`、non-symlink、
許可された basename であることを検査し、filesystem が directory link count を 2 以上に
することを理由に拒否しません。

### Provenance

`agent-canon-static-seed.json` は UTF-8 JSON object とし、key set を次に完全一致させます。

```json
{
  "schema_version": 1,
  "source_commit": "<lowercase 40-or-64-hex Git object id>",
  "source_repository": "iwashita-nozomu/agent-canon"
}
```

`source_commit` は lowercase hexadecimal の 40 または 64 文字だけを許可します。値の
validation に加え、AgentCanon exporter の deterministic serialization（sorted keys、indent
2、UTF-8、末尾 newline 一つ）と bytes が一致することを確認します。branch、remote、日時、
latest 判定、sync history、consumer state は provenance に現れてはなりません。

provenance は maintainer が確認した historical input の attestation であり、importer が
source commit を resolve、fetch、checkout、署名検証、latest 判定する authority ではありません。
payload の reviewed authority は repository-owned な
`tests/fixtures/static-seed-c5fa3a22/` の exact relative path set、各 file の bytes SHA-256、
mode、provenance bytes です。external bundle はこの reviewed fixture から生成した expected
manifest と path-by-path に完全一致しなければ受理しません。provenance
と payload を別 directory・別 commit から混ぜる API はなく、`source_commit` を使った外部
read は実装しません。

このため free-prose の `developer_instructions` を regex で semantic-equivalent と判定する
production gate は持ちません。role の prose は fixture bytes の exact digest 比較で受理され、
fixture を変更しない future seed は受理されません。future seed は先に reviewed fixture
（およびそこから再生成した expected manifest）の変更としてレビューされ、その変更後にだけ
新しい external export が受理されます。schema/header/name、regular-file/mode/type、source-free
prefix、network/credential surface は digest と重複する positive semantic authority ではなく、
typed diagnostic/security boundary です。これらは malformed、危険 surface、symlink、実行可能
object を明確な finding にする最小検査として残し、prose の意味同値を推論しません。

### Config と role closure

`.codex/config.toml` を UTF-8 TOML として parse し、`[agents]` table を必須とします。
`max_threads`、`max_depth`、`job_max_runtime_seconds` は role ではない既存 runtime budget
key として扱い、それ以外の `agents.<role>` は table かつ string `config_file` を持ち、
その値が厳密に `agents/<role>.toml` でなければなりません。role 名は一段 basename に
限定し、separator、`.`、`..`、NUL、空文字を拒否します。

参照 role の集合と bundle の `.codex/agents/*.toml` の集合は完全一致します。missing role、
unreferenced role、duplicate path、config が同じ role を別 file に向ける状態は拒否します。
各 role file は同名 `name` を持つ既存 `generated_role_view_v1` static role payload として
parse し、現行の実行 field set（`name`、`description`、`nickname_candidates`、
`sandbox_mode`、`approval_policy`、`model`、`model_reasoning_effort`、
`developer_instructions`）以外の TOML key を追加しません。実装は既存 role schema の値の
型と static projection digest の読み取りも検証し、別 role の payload 混入を拒否します。

role TOML のコメントは #716 の consumer-static contract に従い、schema marker と
hexadecimal source-canonical digest だけを持つ path-free header にします。live dependency
header、materializer path、registry path、source checkout path は typed diagnostic/security
boundary として拒否します。role の `developer_instructions` は production で semantic
regex 検査しません。fixture の exact bytes が parent assignment、parent-only authority、
validation owner、stop/handback の reviewed contract を所有し、consumer はその exact payload
を読むだけです。

### Semantic prefix and forbidden-surface closure

config、全 role payload、provenance の bytes を lower-case 化し、次の #716 exact producer
prefix を substring として拒否します。

```text
agents/skills/
agents/model_profiles.toml
tools/agent_tools/
../../agents/
../../tools/
```

同じ scan で source/runtime/updater/network/import marker（`vendor/agent-canon`、
`tools/agent-canon`、`agent_canon_source_root`、`agent-canon-update`、
`agent-canon-latest-check`、`git clone`、`git submodule`、`curl `、`wget `、`http://`、
`https://`、`ssh://`、`import agent_tools`、`from agent_tools`、`sync-state`、
`update-state`）を拒否します。credential は generic な `token` substring では検出
しません。bytes marker は `agent_canon_repo_token`、`agent_canon_read_token`、`github_pat_`、
`authorization: bearer`、`begin private key` という typed credential context に限定します。
TOML を再帰的に走査し、exact key name が `command`、`env`、`hooks`、`mcp_servers`、
`network_access`、`remote`、`url`、`token`、`secret`、`credential`、`credentials`、
`update_state` の場合だけ実行・network・secret・sync surface として拒否します。
これにより `token-efficient`、`token-aware`、`tool_output_token_limit` の通常の説明・設定は
typed marker だけでは拒否されません。ただし、それらを含む external payload が reviewed
fixture と bytes 不一致なら exact digest gate で拒否されます。prefix/forbidden scan は prose
keyword の意味を判定するものではなく、危険な source/runtime/network/credential surface を
diagnostic として報告する最小 security boundary です。

### Concrete acceptance fixture

この design の acceptance input は run-local bundle
`workspace/static-seed-c5fa3a22/` です。これは AgentCanon #716 merge commit
`c5fa3a22c8486952dc6dede0cc3a25e5ba7741e5` を provenance に持ち、36 payload files
（`.codex/config.toml` と 35 same-named role TOML）および provenance file 一つからなります。
fixture は source checkout の代替ではなく、import test が fresh export directory として
読む具体的な入力です。実装・test はこの directory を変更せず、同じ path shape の isolated
copy を使って success、no-op、role add/update/delete、prevalidation failure、rollback を
検証します。fixture の absolute execution path は durable design/DIC artifact に保存しません。
Portable test の source authority は repository-owned な
`tests/fixtures/static-seed-c5fa3a22/` です。実装は run-local bundle をこの fixture に反映
した tracked snapshot として追加し、test は `Path(__file__).resolve().parents[1] / "fixtures" /
"static-seed-c5fa3a22"` から読むだけです。developer home、cwd、`workspace/` の absolute
path、AgentCanon checkout を test source にしません。

この fixture は test data であると同時に importer が読む reviewed expected payload authority
です。実装は fixture の repository-relative root を解決し、起動時にその exact path/bytes/mode/
provenance から expected manifest を作ります。external bundle の production API は任意の
free-prose export を一般に受け入れる API ではなく、current reviewed fixture と完全一致する
fresh export の maintainer import です。fixture または manifest の reviewed update なしに
future source commit を受理する fallback、latest resolver、pattern-based compatibility mode は
持ちません。

## Prevalidation と deterministic plan

`main` は次の単一の phase order を守ります。

1. `load_bundle(bundle)` が root shape、path set、mode、provenance、config、role schema、
   exact closure、typed prefix/forbidden-surface diagnostics を検証し、bundle root fd で開いた
   file descriptor の inode/device/size/mode を read 前後に再検証して immutable
   `ValidatedBundle`（source commit、provenance bytes、config bytes、sorted role bytes、
   bundle digest）を memory に作る。次に repository-owned fixture から得た expected manifest
   （exact relative path set、各 bytes SHA-256、mode、provenance digest）と path-by-path に照合
   し、完全一致しない bundle は `TSSI_BUNDLE_EXPECTED_DIGEST` として plan 前に拒否する。
2. `open_target_lock(root)` が `.codex/agents` directory fd を `O_DIRECTORY|O_NOFOLLOW` で
   開き、`flock(LOCK_EX|LOCK_NB)` を取得する。lock は bundle read の後に解放せず、recovery、
   target read、plan、apply、readback、journal cleanup の全期間を所有する。別 importer が
   lock を保持していれば待機せず、`TSSI_CONCURRENT_IMPORT`、exit 75、target unchanged を
   deterministic に返す。bounded timeout、background retry、hidden wait は実装しない。
3. lock を保持したまま `recover_interrupted_transaction(root)` を先に実行する。残留 journal
   がなければ `read_target_state(root)` が controlled target の current bytes、mode、存在有無を
   読み、root shape と symlink/non-regular safety を検証する。target 外の path は read-only でも
   判断材料にしない。残留 journal が不正、複数、または backup が欠けている場合は fail-closed
   とし、既存 target を変更せず recovery finding を返す。
4. `revalidate_bundle_fds(validated_bundle)` が保持中の各 bundle fd を rewind/read し、digest、
   device/inode、mode、size を最初の `ValidatedBundle` と比較する。同時に bundle root、
   `.codex`、`.codex/agents` の各 directory fd の device/inode/mode/type と、各 directory
   の exact entry tuple `(name, device, inode, mode, type)` set を fd-based に再走査し、最初の
   snapshot と比較する。差分があれば（unexpected add/remove/rename/type change を含む）
   `TSSI_BUNDLE_RACE`、exit 2、target unchanged とし、同じ inode への in-place mutation も
   受け入れない。この re-read は journal 作成/stage の直前に行い、さらに backup 完了後・
   live apply の直前にも同じ digest/metadata revalidation を行う。以後 apply が使う staged
   bytes は最後の revalidated fd snapshot からだけ作る。
5. `build_plan(validated_bundle, target_state)` が sorted path order で create、replace、
   stale-delete、no-op を決める。plan は bundle digest、source commit、old/new path set、
   old/new bytes digest、write set を含み、ここまで filesystem mutation はゼロです。
6. plan が空なら `no-op` を返し、temporary directory、backup、chmod、replace、unlink を
   行いません。
7. non-empty plan だけが transaction phase へ進みます。

prevalidation failure は typed `TSSI_BUNDLE_*` または `TSSI_TARGET_*` finding を stderr に
一行で出し、exit 2 とします。入力が壊れている場合、destination tree、target snapshot、
provenance、stale role のいずれにも部分変更を残しません。

## Apply、rollback、readback

transaction は target と同じ filesystem 上の private durable journal directory を使います。
journal は `.codex/.static-seed-import.<nonce>.txn/` の一時 surface であり、static seed の
payload、updater state、sync history ではありません。成功後は必ず消しますが、crash 後に
recovery が必要な間は残ります。journal は target と同じ filesystem に `mkdir` し、cross-device
rename を使いません。lock directory fd、journal fd、bundle fd、target directory fd を保持し、
全 path operation は `openat` / `renameat` / `unlinkat` 相当と `O_NOFOLLOW` で行います。

`manifest.json` は exact top-level key set
`{schema_version, transaction_id, source_commit, bundle_sha256, old, new, plan, state, expected_stage,
expected_backup}` だけを持ちます。`old` と `new` は controlled relative path を key とする
map で、各 entry の exact key set は `{exists, sha256, size, mode, device, inode, type}` です。
absent entry も `exists=false`、他の値は null、`type="absent"` として表し、key の追加・欠落・
型違い・unknown path・old/new の片側だけの path は `TSSI_JOURNAL_MALFORMED` です。manifest
の新旧 closure をこの exact schema で検証できない限り、state 名や directory の存在から
意味を推測しません。journal 作成直後に pre-state と expected stage path/digest/mode/type を
predeclare して、`manifest` を atomic file として durable 化
します。この `predeclared` state は construction-incomplete です。staged/backup bytes は
それぞれ `stage.partial/` と `backup.partial/` に書き、partial directory は live apply の
所有権を意味しません。

manifest schema の値域も固定します。`schema_version` は JSON integer `1` のみ（`true`/`false`
や文字列は不可）、`state` は `predeclared | ready | backup_constructing | backed_up | applied |
read_back | committed | rolled_back | rollback_failed` の enum、`transaction_id` は
`static-seed-[0-9a-f]{32}` の lower-case string、`source_commit` は lower-case 40/64 hex、
`bundle_sha256` と全 `sha256` は exactly 64 lower-case hex です。path は canonical relative
POSIX string で、allowed controlled set
`{agent-canon-static-seed.json, .codex/config.toml, .codex/agents/<role>.toml}` の一段 role
path 以外を許しません。top-level manifest に `plan` を追加し、exact key set は
`{schema_version, transaction_id, source_commit, bundle_sha256, old, new, plan, state,
expected_stage, expected_backup}` とします。`plan` は exact key set
`{added, updated, deleted, write_order}` の object で、各値は sorted unique path string list、
`write_order` は plan path の permutation、三つの差分 list は相互排他的です。extra/missing
key を拒否します。

`old`/`new` は同じ complete controlled path key set を持ち、各 entry は exact key set
`{exists, sha256, size, mode, device, inode, type}` です。両 map の `exists` は JSON boolean、
存在する regular payload の `sha256` は exactly 64 lower-case hex、`size` は integer `>=0`、
`mode` は integer `0644`（JSON値 `420`）、`type="regular"` です。old の exists=true は
`device`/`inode` positive integer であり、new の exists=true は `predeclared`、`ready`、
`backup_constructing`、`backed_up` 中だけ device/inode null を許し、`applied` 以降は positive
integer でなければなりません。欠損 entry は `sha256=null,size=null,mode=null,device=null,
inode=null,type="absent"` です。empty file は `size=0` と SHA-256 of empty bytes（空文字列では
ない）を持ちます。`exists=true` の sha/size/mode/type 欠落、old の device/inode null、phase
不整合、`exists=false` で non-null、mode/type違い、duplicate/extra/missing path、old/new の
片側だけの path は全て `TSSI_JOURNAL_MALFORMED` です。old は lock 下の prevalidation target snapshot を
`predeclared` 作成前に bind し、以後変更しません。new の bytes/size/mode/type は plan 時に
bind しますが、new device/inode は live target に存在しないため `predeclared`、`ready`、
`backup_constructing`、`backed_up` 中は null です。全 live replace/delete 後、最後の target
fd revalidation で存在する new regular file の device/inode を bind（new-only delete は absent
null のまま）し、`applied` manifest として atomic replace/fsync します。従って `applied`、
`read_back`、`committed` では exists=true の new device/inode が positive、absent は null で
なければなりません。

`expected_stage` と `expected_backup` は exact key set
`{paths, digests, tree_sha256, marker, published}` の object です。`paths` は sorted unique
relative journal payload paths、`digests` は paths と完全一致する map（各値 exactly 64
lower-case hex）、`tree_sha256` は closure-complete なら exactly 64 hex、construction-incomplete
なら null、`marker` は literal `"COMPLETE"`、`published` は JSON boolean です。stage の paths/
digests は new exists=true entry と完全一致し、backup は old exists=true entry と完全一致し、
それぞれの extra/missing/duplicate path、map/list 不一致、marker/published/tree digest の
矛盾を拒否します。manifest の nested object/list の型違い、range違反、余分な key、closure
不一致は全て `TSSI_JOURNAL_MALFORMED` です。

### Durable state truth table

次の表が state validator の唯一の許可集合です。stage tuple は
`(published, partial, consumed, COMPLETE)`、backup tuple は
`(published, partial, COMPLETE)`、`R` は durable `rollback-required`、`M` は durable
`committed` marker、tree verify は required readback です。`subset` は manifest の known
closure の proper-or-equal subset、`exact` は expected path/digest/mode/type と完全一致を
意味します。表にない組み合わせ（特に published=false の曖昧な fallback）は malformed として
保持します。

| manifest state / cleanup tomb preserved_state | stage tuple allowed | backup tuple allowed | R | M | tree digest/readback required | normal transition or recovery result |
| --- | --- | --- | --- | --- | --- | --- |
| `predeclared` | `(0,0,0,0)` or `(0,1,0,0/1)`; crash exception `(1,0,0,1)` | `(0,0,0)` | `0` | `0` | pre-state exact; partial stage `subset` when present | construct stage; published-stage exception persists `ready`, then cleanup-only |
| `ready` | `(1,0,0,1)` | `(0,0,0)` | `0` | `0` | pre-state exact + stage `exact` | enter `backup_constructing` only after durable state update |
| `backup_constructing` | `(1,0,0,1)` | `(0,0,0)` or `(0,1,0/1)`; crash exception `(1,0,1)` | `0`; exception `1` | `0` | pre-state exact + stage `exact`; backup `subset` when partial | construct backup; published-backup exception persists `backed_up`, then rollback/cleanup-only |
| `backed_up` | `(1,0,0,1)` | `(1,0,1)` | `1` | `0` | pre-state exact + stage/backup `exact` | live apply may start |
| `applied` | `(1,0,1,1)` | `(1,0,1)` | `1` | `0` | candidate path/bytes/mode exact; new bindings positive | persist `read_back` after post-readback |
| `read_back` | `(1,0,1,1)` | `(1,0,1)` | `1` | `0` | candidate, provenance, fixture digest and write-set exact | persist `committed` marker/state |
| `rolled_back` | `(1,0,0/1,1)` | `(1,0,1)` | `1` | `0` | pre-state exact | create cleanup tomb; return rollback failure, never apply |
| `rollback_failed` | `(1,0,0/1,1)` | `(1,0,1)` | `1` | `0` | unknown/incomplete pre-state; no cleanup proof | retain journal fail-closed; tomb creation is illegal |
| `committed` | `(1,0,1,1)` | `(1,0,1)` | `1` | `1` | candidate + fixture digest exact | cleanup may return recovered `pass` |
| `cleanup.pending(predeclared)` | same as legal `predeclared` row, never published-stage exception | same as legal `predeclared` row | `0` | `0` | pre-state exact | cleanup-only failure |
| `cleanup.pending(ready)` | `(1,0,0,1)` | `(0,0,0)` | `0` | `0` | pre-state + stage exact | cleanup-only failure |
| `cleanup.pending(backup_constructing)` | same as non-exception `backup_constructing` row | same as non-exception row | `0` | `0` | pre-state + known partial closure | cleanup-only failure |
| `cleanup.pending(rolled_back)` | same as `rolled_back` row | same as `rolled_back` row | `1` | `0` | pre-state exact | cleanup-only failure |
| `cleanup.pending(committed)` | same as `committed` row | same as `committed` row | `1` | `1` | candidate + fixture digest exact | cleanup-only recovered `pass` |

`cleanup.pending(backed_up|applied|read_back|rollback_failed)`、unknown state、manifestless
tomb、orphan marker、published closure with a missing/extra required marker are not rows in the
allowed set and return `TSSI_JOURNAL_MALFORMED` while retaining journal/tomb. `consumed=1` is bound
only after all live replacements have completed and the staged bytes have been read; it never means
that the stage directory may be ignored before cleanup. `R=1` is required for every rollback-capable
state and cannot be inferred from backup publication alone. The two and only two crash exceptions in
the table are the predeclared/published-stage row and the backup_constructing/published-backup row.

この表が normative invariant です。construction closure は `published=false` except exactly
the two rows marked crash exception（predeclared/published-stage と
backup_constructing/published-backup）であり、それ以外の published closure、required marker
欠落、余分 marker は `TSSI_JOURNAL_MALFORMED` として保持します。

state-closure validator の順序は固定します。(1) manifest、marker、directory、entry list の
base shape/type/range を検証し、(2) 次の crash-window transition を先に認識し、(3) 認識した
遷移または通常 state に対して closure、marker、target invariant を検証します。従って
directory の存在だけを通常 state と解釈したり、異常を先に malformed として crash-window
branch を失うことはありません。

- `state=predeclared` で published `stage/` が完全 closure（`COMPLETE`、expected path/digest/
  mode/type 一致）、published `backup/` がなく、`rollback-required` もない場合は、stage
  publication と `ready` state update の間の crash window です。live target が pre-state と
  exact 一致することを再検証し、manifest を `ready` に atomic replaceして file/journal/parent
  fsync した後、同一 invocation では apply せず cleanup-only failure を返します。
- `state=backup_constructing` で published `backup/` が完全 closure、`COMPLETE` と
  `rollback-required` が durable、`backed_up` state がまだない場合は、rollback-required と
  `backed_up` update の間の crash window です。live target が pre-state と exact 一致することを
  再検証し、manifest を `backed_up` に atomic replaceして fsync した後、同一 invocation では
  apply せず rollback/cleanup-only failure を返します。
- published closure と required marker の組み合わせが一致しない場合（published stage の
  `COMPLETE` 欠落、backup の `COMPLETE` 欠落、published backup の `rollback-required` 欠落、
  rollback-required 単独、expected 外の marker、marker だけの orphan、両 closureの余分な
  marker）は crash window と認識せず `TSSI_JOURNAL_MALFORMED` として journal を保持します。
  marker の存在から closure を推測せず、marker を削除して live apply を始めません。

stage は全 expected entry を `O_CREAT|O_EXCL` で書き、各 bytes/mode/type/digest を検証し、
`COMPLETE` marker を最後に fsync して `stage.partial` を `stage/` へ atomic rename します。
`stage/` の存在と marker の digest 一致が closure-complete の証拠であり、その後にだけ
manifest state を `ready` へ更新します。従って `ready` は staged closure を必ず含み、
`predeclared`/partial を ready と解釈しません。backup も同じ形式で `backup.partial/` から
`backup/` へ closure publication します。backup closure 後に `rollback-required` marker を
fsync し、その marker と complete backup の両方が揃った後にだけ manifest state を `backed_up`
へ更新します。従って `backed_up` は complete backup と first rollback-required point を
同時に意味し、live apply の前提になります。

manifest state は atomic replace し、各 state update、blob write、directory entry を fsync
した後に親 directory を fsync します。

exact fsync/commit order は次です: (a) journal mkdir → parent fsync、(b) predeclared manifest
write → file fsync → journal fsync、(c) stage partial blobs → each file fsync、`COMPLETE`
marker fsync、partial directory fsync、partial→published directory rename、journal fsync、
(d) `ready` update → manifest fsync → journal/parent fsync、(e) `ready` を
`backup_constructing` へ atomic manifest replace → manifest file fsync → journal directory fsync
→ journal-parent fsync、(f) その三段 fsync 完了後に初めて `backup.partial/` を mkdir → partial
directory fsync → journal/parent fsync、(g) backup blobs → each file fsync、`COMPLETE` marker
fsync、partial directory fsync、partial→published directory rename、journal fsync、(h) backup
publication 後に `rollback-required` marker fsync、(i) `backed_up` update → manifest fsync →
journal/parent fsync、(j) each live replace/unlink → affected `.codex` and root directories
fsync、(k) `applied` update → manifest/journal/parent fsync、(l) post-readback pass 後に
`committed` marker/state を同じ順で fsync、(m) journal removal → parent fsync。closure marker、
rollback-required marker、committed marker より前に対応する directory/journal を消しません。

ここで `backup_constructing` は backup.partial の存在を表すのではなく、ready から backup
construction の所有権を取得した durable state です。従って backup.partial の mkdir は
この state publication と三段 fsync が完了した後にだけ許可されます。state graph も
`ready --(manifest/file+journal/parent fsync)--> backup_constructing --(partial mkdir/fsync)--> backup.partial`
の順序を固定します。

journal を消す前の cleanup は state-preserving `cleanup.pending` tomb を使います。tomb は
exact key set `{schema_version, transaction_id, manifest_sha256, preserved_state, action,
delete_set, deleted}` だけを持ちます。`schema_version` は JSON boolean ではない integer `1`、
`transaction_id`/`manifest_sha256` は manifest と同値、`preserved_state` は manifest state enum
の値、`action` は literal `"cleanup"`、`delete_set` と `deleted` は journal-relative path の
sorted unique string list です。両 list は manifest と tomb 自身を含まず、stage/backup/blob/marker
の known cleanup entries だけを含みます。`deleted` は `delete_set` の subset です。payload
entries を全て削除して tomb を消し、最後に manifest と journal directory を処理する順序を
固定します。noncommitted state の cleanup intent を `committed` に昇格させることは禁止します。

tomb は atomic replace → tomb file fsync → journal directory fsync → journal-parent fsync の順で
durable 化し、その後に `delete_set` を deterministic order で削除します。各 unlink 成功後に
`deleted` を更新して同じ順序で tomb を再度 durable 化します。entry deletion、tomb deletion、
manifest deletion、journal directory removal の各 crash boundary は下表の通りです。
次回 invocation は tomb と manifest を exact key closure、transaction id、manifest digest、
preserved_state、known remaining entry set に照合します。

| cleanup boundary | required durable evidence | recovery oracle |
| --- | --- | --- |
| tomb durable before first entry deletion | valid tomb + complete manifest | target/candidate state matches preserved state; delete only known `delete_set`; preserve failure/pass result |
| entry deletion in progress | tomb `deleted` subset + manifest | actual entries are exactly a remaining known subset; reconcile and continue cleanup-only |
| all entries deleted, tomb still present | tomb with `deleted == delete_set` + manifest | remove tomb, then continue to manifest removal; no plan/apply |
| tomb removed before manifest deletion | manifest terminal state, no tomb | verify terminal state and remove manifest only; if crash leaves orphan directory, retain unknown fail-closed |
| manifest deletion in progress/complete | no tomb and possibly no manifest | empty or markerless journal is orphan/unknown and is retained fail-closed; never infer committed |
| journal directory removal in progress/complete | no owned files or unknown residue | successful removal is done; residue is orphan/unknown and cannot be applied or committed |

`predeclared`/`ready`/`backup_constructing` cleanup tombs require exact pre-state proof and return
cleanup failure after recovery. `rolled_back` has the same failure result after pre-state readback;
`committed` returns recovered `pass` only after candidate readback. `backed_up`、`applied`、
`read_back` は cleanup に到達せず、必ず rollback を完了して `rolled_back` を durable 化して
から tomb を作ります。`rollback_failed`、`malformed`、`unknown` も安全な cleanup intent を
持たず journal を保持します。従ってこれらの state の tomb は parser が認識しても illegal
state combination として `TSSI_JOURNAL_MALFORMED` を返し、削除を開始しません。これは
logical に cleanup されない state の到達不能根拠です。manifestless tomb、malformed tomb、
unknown preserved_state、digest mismatch は `TSSI_JOURNAL_MALFORMED` として保持し、
manifestless tomb を committed 扱いにしません。cleanup intent の tomb も plan/apply を開始
する理由にはなりません。

preserved_state ごとの tomb 到達性は次で固定します。legal 行は上の tomb crash matrix の
durable-after-entry-deletion、manifest-deletion、directory-removal 各 oracle を適用し、
illegal 行は tomb を作らず、観測時も fail-closed です。

| preserved_state | tomb creation | tomb/manifest/dir crash oracle |
| --- | --- | --- |
| `predeclared` | legal: exact pre-state + known construction cleanup | cleanup-only failure; no target apply |
| `ready` | legal: exact pre-state + published stage cleanup | cleanup-only failure; no target apply |
| `backup_constructing` | legal: exact pre-state + partial-or-empty backup cleanup | cleanup-only failure; no target apply |
| `backed_up` | illegal: rollback must complete first | `TSSI_JOURNAL_MALFORMED`, retain journal/tomb |
| `applied` | illegal: candidate must rollback or commit first | `TSSI_JOURNAL_MALFORMED`, retain journal/tomb |
| `read_back` | illegal: only committed transition is allowed | `TSSI_JOURNAL_MALFORMED`, retain journal/tomb |
| `rolled_back` | legal: exact pre-state is durable | cleanup-only failure; no target apply |
| `rollback_failed` | illegal: unresolved recovery evidence | retain fail-closed; never delete |
| `committed` | legal: exact candidate readback | cleanup-only recovered `pass` |

`recovery_cleanup` は manifest state/preserved_state ではなく action output であり、tomb value
としては不許可です。これにより enum にない synthetic state や cleanup からの committed 昇格を
排除します。

### Durable transition crash matrix

| crash boundary | last durable evidence | live target | next invocation action |
| --- | --- | --- | --- |
| journal mkdir before manifest | no ownership/pre-state | unchanged | empty/unknown journal is retained fail-closed; no apply |
| `predeclared` manifest durable before first partial directory | manifest pre-state plus declared closure, no partial directory | unchanged | verify exact pre-state and journal contains only manifest/declared closure; cleanup-only, then stop |
| `predeclared` manifest during partial stage/backup | manifest pre-state plus known expected closure | unchanged | verify exact pre-state and known-subset ownership; cleanup partial only, then stop |
| `stage/` publication before `ready` state | complete stage marker and exact stage closure | unchanged | verify closure, promote `ready` if needed, cleanup-only, then stop |
| `ready` state | complete published stage closure | unchanged | verify pre-state and closure, cleanup-only, then stop |
| `backup_constructing` after state fsync but before `backup.partial/` mkdir | ready closure plus backup-construction state; no partial directory | unchanged | verify exact pre-state and journal has no unknown entry; cleanup-only, then stop |
| `backup.partial/` before backup closure | known backup subset plus pre-state | unchanged | verify known subset and pre-state, cleanup partial, then stop |
| complete `backup/` + `rollback-required` before `backed_up` state | complete backup and first rollback point | unchanged | verify closure, promote `backed_up` if needed, rollback/cleanup-only, then stop |
| `backed_up` before first live replace | complete backup + rollback point | unchanged | exact backup replay/readback, mark `rolled_back`, cleanup, then stop |
| any live replace/unlink before `applied` | complete backup + rollback point | possibly partial | reverse replay backup, exact pre-state readback, or retain fail-closed |
| `applied` before `committed` | complete candidate plus rollback point | candidate or partial | verify candidate; commit only if marker/readback is durable, otherwise rollback |
| `committed` before journal removal | commit marker and candidate readback | complete candidate | verify candidate, remove journal, return recovered `pass`; if removal fails, retain candidate+journal and return cleanup failure, never rollback |
| noncommitted `cleanup.pending` tomb before journal removal | tomb preserves `predeclared`/`ready`/`backup_constructing`/`rolled_back` plus manifest digest | pre-state or recovery evidence | verify tomb+manifest; cleanup-only with preserved failure state; never promote to committed |
| manifestless/malformed cleanup tomb | tomb without trustworthy ownership | unknown | retain journal/tomb, return `TSSI_JOURNAL_MALFORMED`; never infer committed candidate |

Every transition is one atomic manifest/marker publication followed by the specified fsyncs. A
missing marker is never inferred from a directory that merely exists; a complete closure marker is
required before `ready` or `backed_up` is recognized.

apply は次の順序です。

1. plan の全 new bytes を journal の `stage.partial/` に `O_CREAT|O_EXCL` で stage し、expected
   digest、mode、inode/device を read back する。closure marker と published `stage/` を作り、
   manifest を `ready` にする前に live path を変更しない。
2. existing controlled file を `backup.partial/` に bytes、mode、inode/device、存在状態、path
   order 付きで保存する。backup closure publication、`rollback-required` marker、`backed_up`
   state の durable 化の前に live path を unlink/replace しない。
3. sorted path order で new config、new role、new provenance を同じ filesystem の
   `renameat` 相当で置き、各 file を `0644` にする。直前の inode/device と lock-held target
   state が一致しなければ apply を開始せず reject する。
4. bundle にない stale direct `*.toml` role を backup journal と照合して `unlinkat` する。
5. controlled path set、bytes、mode、provenance source commit、reviewed-fixture expected
   digest、config-role closure、typed security diagnostics を live target から再検証し、pass
   の後にだけ `committed` marker を durable 化する。free-prose semantic equivalence はここで
   も判定しない。

### Descriptor、symlink、TOCTOU、concurrency contract

bundle root、`.codex`、`.codex/agents` は `O_DIRECTORY|O_NOFOLLOW` で fd を開き、各 entry
はその parent fd に対する `openat` 相当で `O_NOFOLLOW|O_CLOEXEC` を付けて開きます。regular
file は `fstat` の device、inode、mode、size、link count を bytes read 前後で比較し、fd から
読み取った bytes を plan に bind します。各 revalidation は三つの directory fd の
device/inode/mode/type と、root → `.codex` → `.codex/agents` の exact entry tuple
`(name, device, inode, mode, type)` set を fd-based に再走査します。初回 snapshot にない add、削除、rename、type change、
directory fd identity change は全て `TSSI_BUNDLE_RACE` です。path を resolve してから再度
pathname で読む実装は許可しません。

target は `.codex/agents` directory fd の exclusive `flock` を最初に取得します。lock を
保持したまま controlled path を fd/dirfd で列挙し、各 planned path の device、inode、mode、
size、existence を snapshot します。apply の直前と各 replace/delete の直前に `fstatat`
相当の `AT_SYMLINK_NOFOLLOW` revalidation を行い、外部 actor が lock を尊重しない場合の
変更も検出します。期待値と違えば apply を開始せず、または durable journal から rollback
し、target 外 path を触りません。target config/role/provenance の symlink swap、bundle
directory/file swap、同時 importer は race/concurrency finding として扱います。

replace、delete、mode change、post-readback のいずれかが失敗したら、journal を逆順に replay
し、元の bytes/mode/existence を復元し、new-only path を削除します。rollback 後に live
controlled snapshot を pre-import state と byte-for-byte/mode-for-mode に比較し、journal
state を `rolled_back` として durable 化してから journal を消し、`TSSI_ROLLBACK=pass` を
含む failure を返します。rollback の検証まで完了しない限り `pass` を返しません。rollback
自体が失敗した場合は `TSSI_ROLLBACK=failed` とし、journal を残して次回 invocation の
fail-closed recovery に委ねます。成功扱い、silent warning、partial tree の隠蔽を許しません。

### Crash と restart recovery

process kill、power loss、Python exception を同じ crash class とします。次の invocation は
必ず lock acquisition 後、plan より前に journal の manifest state を読む。

- `predeclared` with no partial directory, or with `stage.partial/`, is construction-incomplete.
  `backup.partial/` under predeclared is impossible under the durable state order and is retained as
  `TSSI_JOURNAL_MALFORMED`. Recovery first proves the live target is byte/mode/path/inode-equal to
  the pre-state declared in the manifest and that the journal contains no unknown entry beyond the
  manifest and declared stage closure. When `stage.partial/` exists, every entry must be a known
  subset with matching digest/type/ownership, and no published closure or rollback marker may be
  mixed with it. With no partial directory, exact pre-state plus no-unknown proof is sufficient for
  cleanup-only recovery; no directory is invented. If proofs pass, it removes only known construction,
  fsyncs the journal parent, returns `TEMPLATE_STATIC_SEED_IMPORT=fail recovery=cleaned_predeclared`,
  exit 1, and never starts plan/apply in the same invocation. Missing or inconsistent evidence retains
  the journal and fails closed.
- `ready` with published `stage/`: staged closure must be complete: marker, exact expected path set,
  bytes/mode/type/inode metadata, and stage digest all match the predeclared manifest. Recovery does
  not apply it; it removes the complete staged construction only after live pre-state exact readback,
  fsyncs the parent, returns `TEMPLATE_STATIC_SEED_IMPORT=fail recovery=cleaned_ready`, exit 1, and
  requires an explicit rerun. A missing/invalid closure is retained and fails closed. A published
  stage with a still-`predeclared` manifest is promoted to `ready` only after the same closure proof,
  then stops; it never begins live apply.
- `backup_constructing`: this state is durable before `backup.partial/` mkdir, so recovery accepts
  either no partial directory or a known, digest-checked subset. In both cases live target must still
  equal pre-state and the journal must have no unknown entry. With no partial directory, cleanup-only
  recovery removes no invented path and exits `TEMPLATE_STATIC_SEED_IMPORT=fail
  recovery=cleaned_backup_constructing`, exit 1. With a partial directory, it removes only that
  known construction and exits the same way. A published
  `backup/` with durable `rollback-required` but without `backed_up` is promoted only after complete
  closure proof, then treated as rollback/cleanup-only and exits 1; it never starts live apply.
  A published `backup/` without durable `rollback-required` is closure-inconsistent and is retained
  fail-closed; it is never treated as `backed_up`.
- `backed_up` / `applied`: `backup/` exact closure and durable `rollback-required` marker are required.
  `committed` marker がないため、backup を逆順 replay し、pre-state を exact readback して
  `rolled_back` を durable 化し、journal を消します。これは
  `TEMPLATE_STATIC_SEED_IMPORT=fail recovery=rolled_back`、exit 1 であり、`noop` でも
  `pass` でもありません。復元できない場合は journal を保持して
  `TSSI_RECOVERY=failed` を返し、target をさらに変更しません。
- `rolled_back`: pre-state の digest、path set、mode を再検証します。一致すれば journal を
  cleanup して `TEMPLATE_STATIC_SEED_IMPORT=fail recovery=rolled_back`、exit 1 を返します。
  不一致なら journal を保持して fail-closed です。
- `rollback_failed`: backup、manifest、target を自動削除・上書きせず、journal を保持して
  `TEMPLATE_STATIC_SEED_IMPORT=fail recovery=rollback_failed`、exit 1 を返します。次の
  invocation もこの state を解決できるまで plan/apply を開始しません。
- `committed`: candidate の path set、bytes、mode、source/bundle digest を再検証します。
  一致すれば journal の remove だけを試み、成功時は通常の `pass` line に
  `recovered=committed` と counts を付けて exit 0 を返します。これは transaction の commit
  回復であり `noop` ではありません。remove journal が失敗しても complete candidate を
  rollback せず、candidate と journal を保持して
  `TEMPLATE_STATIC_SEED_IMPORT=fail recovery=committed_cleanup`、exit 1 を返します。次の
  invocation は同じ committed candidate を再検証して cleanup だけを再試行します。
  candidate の bytes/mode/source digest が不一致なら完全な backup がある場合だけ pre-state
  を restore して `rolled_back` に遷移し、そうでなければ journal を保持して fail-closed
  します。
- `cleanup.pending` tomb: tomb の exact key closure、manifest digest、transaction id、
  `preserved_state` を先に検証します。`predeclared`/`ready`/`backup_constructing`/`rolled_back`
  は pre-state exact readback 後に known cleanup だけを再試行して failure を返し、
  `rollback_failed` は何も推測せず保持します。`committed` は candidate exact readback 後に cleanup だけを再試行し、成功
  時だけ recovered `pass` です。tomb が manifestless、malformed、unknown state、digest
  mismatch なら `TSSI_JOURNAL_MALFORMED` として保持し、candidate を committed と解釈せず、
  plan/apply も開始しません。
- `malformed` / `unknown` / 複数 journal: manifest state、digest、path、backup closure、marker を
  確認できないため、journal と target を変更せず `TSSI_RECOVERY=malformed` または
  `TSSI_RECOVERY=unknown`、exit 1 を返します。人手で journal を解決するまで live apply
  を開始しません。

この順序により commit marker のない live partial state は必ず pre-state へ戻り、marker の
ある candidate は exact readback なしに成功扱いになりません。recovery phase は cleanup または
rollback だけを行い、新しい live apply を同一 invocation で開始しません。lock は directory fd の
kernel lock なので crash 時に自動解放され、残留 lock path を stale 判定する必要がありません。

filesystem の atomic rename は一 file 単位なので、multi-file の atomicity はこの validated
plan + complete durable journal + exclusive directory lock + crash recovery + reverse replay +
post-readback の transaction invariant で定義します。適用失敗、process crash、再起動 recovery、
post-readback failure injection が pre-import snapshot を完全復元することを test oracle とします。

成功時は次の stable result line を一つ出します。

```text
TEMPLATE_STATIC_SEED_IMPORT=pass source_commit=<id> roles=<n> added=<n> updated=<n> deleted=<n>
```

同一 bundle の再適用は plan が空となり、次の no-op line だけを出します。

```text
TEMPLATE_STATIC_SEED_IMPORT=noop source_commit=<id> roles=<n> added=0 updated=0 deleted=0
```

## State、failure semantics、invariants

```text
unread -> validated -> planned -> staged -> applied -> read_back -> committed
unread|validated|planned -> rejected
staged|applied|read_back -> rolling_back -> rolled_back|rollback_failed
predeclared -> ready --(atomic manifest + file/journal/parent fsync)--> backup_constructing
backup_constructing --(partial mkdir + fsync)--> backup.partial -> backed_up -> applied -> read_back -> committed
predeclared|backup_constructing -> recovery_cleanup -> (stop; explicit rerun)
ready -> recovery_cleanup -> (stop; explicit rerun)
backed_up|applied -> recovery_rollback -> rolled_back|rollback_failed
committed -> recovery_verify -> (pass recovered=committed)|recovery_rollback
predeclared|ready|backup_constructing|rolled_back|committed -> cleanup.pending -> recovery_verify_preserved_state
rollback_failed -> recovery_blocked
manifestless_tomb|malformed_tomb -> recovery_blocked
malformed|unknown -> recovery_blocked

crash-window exception branches:
`predeclared + published(stage) + COMPLETE + no rollback-required`
  -> verify pre-state -> persist ready -> cleanup-only failure
`backup_constructing + published(backup) + COMPLETE + rollback-required + no backed_up`
  -> verify pre-state -> persist backed_up -> rollback/cleanup-only failure
published closure/marker mismatch or extra marker -> malformed (retain)
```

| finding | phase | required result |
| --- | --- | --- |
| `TSSI_BUNDLE_ROOT` / `TSSI_BUNDLE_UNEXPECTED_PATH` | prevalidation | exit 2; target untouched |
| `TSSI_BUNDLE_ROOT_SYMLINK` / `TSSI_BUNDLE_DIRECTORY_SYMLINK` / `TSSI_BUNDLE_FILE_SYMLINK` | prevalidation | exit 2; target untouched |
| `TSSI_BUNDLE_NONREGULAR` / `TSSI_BUNDLE_MODE` / `TSSI_BUNDLE_EXPECTED_DIGEST` | prevalidation | exit 2; target untouched |
| `TSSI_BUNDLE_PROVENANCE` / `TSSI_BUNDLE_CONFIG` / `TSSI_BUNDLE_ROLE_CLOSURE` | prevalidation | exit 2; target untouched |
| `TSSI_BUNDLE_FORBIDDEN_PREFIX` / `TSSI_BUNDLE_FORBIDDEN_SURFACE` | prevalidation | exit 2; target untouched |
| `TSSI_TARGET_SHAPE` / `TSSI_TARGET_SYMLINK` / `TSSI_TARGET_UNSAFE_ENTRY` | target read | exit 2; target untouched |
| `TSSI_BUNDLE_RACE` / `TSSI_TARGET_RACE` | descriptor/lock validation | exit 2; no uncontrolled write |
| `TSSI_CONCURRENT_IMPORT` | nonblocking directory-fd lock | exit 75 immediately; no target/journal mutation |
| `TSSI_STAGE_WRITE` / `TSSI_APPLY_WRITE` / `TSSI_READBACK` | transaction | reverse replay; exit 1 only after rollback readback |
| `TSSI_JOURNAL_MALFORMED` | manifest/tomb exact-key or ownership read | exit 1; journal/tomb retained; never infer committed |
| `TSSI_RECOVERY` / `TSSI_ROLLBACK` | crash/restart or rollback | exit 1, journal retained on failure; never report import success |
| `TSSI_NOOP` | plan | no filesystem mutation; exit 0 |

The implementation must preserve these invariants:

- `TSSI-001`: One explicit template-owned command accepts only a maintainer-attested export directory
  whose observable closure is validated; it has no source/remote/latest/updater/network/secret/checkout
  input or dependency.
- `TSSI-002`: The accepted bundle has exact reviewed-fixture path, bytes SHA-256, provenance, and
  mode closure, plus same-named role closure, regular `0644` files, no symlink/gitlink/nested/
  unexpected entry, and #716 static role schema. Free-prose semantic equivalence is not an acceptance
  authority.
- `TSSI-003`: All five #716 producer prefixes and source/runtime/updater/network/secret/TOML-key
  surfaces are retained only as typed diagnostic/security boundaries and are rejected before target
  mutation; exact fixture digest remains the payload authority.
- `TSSI-004`: The importer writes only `agent-canon-static-seed.json`, `.codex/config.toml`, and
  `.codex/agents/*.toml`; role additions, updates, and stale deletions share one deterministic plan.
- `TSSI-005`: Every prevalidation failure leaves target bytes, modes, and path set untouched.
- `TSSI-006`: Apply uses same-filesystem durable staging, a complete backup journal, an exclusive
  directory-fd lock, and commit marker/restart recovery; apply/readback failure reverses to the exact
  pre-import snapshot and never reports partial success. After `committed` is durable, cleanup failure
  retains the complete candidate and journal for committed-only retry and never rolls it back.
  Construction-incomplete partial journals are
  distinct from closure-complete `ready`/`backed_up` states and are cleaned only after ownership and
  exact pre-state proof; the journal manifest has closed schema values, old/new invariants, plan and
  stage/backup closure mappings. State-preserving cleanup tombs recover only legal noncommitted
  cleanup intent, and manifestless/malformed tombs or unknown old/new key closure remain fail-closed.
- `TSSI-007`: Post-readback verifies exact bytes/modes, source commit, role closure, reviewed-fixture
  digest, write-set boundary, and positive new device/inode bindings after live apply before success;
  it does not infer developer-instruction semantic equivalence from regex.
- `TSSI-008`: Reapplying identical bundle is a no-op with zero temporary/live writes.
- `TSSI-009`: Bootstrap, fresh-clone, CI, Docker, and runtime paths never invoke or require importer;
  static role instructions retain parent-only assignment, authority, and handback semantics, while
  a concurrent importer is rejected immediately by the nonblocking lock and symlink/TOCTOU races are
  rejected without an uncontrolled write. Every bundle-root, `.codex`, and `.codex/agents` revalidation
  compares the exact entry tuple `(name, device, inode, mode, type)` set, including mode changes.
- `TSSI-010`: Command output and documentation identify source commit and added/updated/deleted role
  counts without adding sync state, branch, timestamp, or latest tracking.
- `TSSI-011`: Portable tests use only the repository-owned static-seed fixture and repository-relative
  resolution; developer absolute paths, cwd-dependent inputs, and AgentCanon checkout ownership are
  not test authorities.

## Side-effect map

| stage | owner | allowed operation | resulting state | evidence |
| --- | --- | --- | --- | --- |
| read | importer | read bundle and controlled target | immutable validated inputs | typed finding or `ValidatedBundle` |
| plan | importer | compare digests and path sets in memory | deterministic transaction plan | plan digest and counts |
| lock/recovery | importer | hold `.codex/agents` directory fd lock and recover durable journal | one importer owns target or fail-closed recovery | lock/recovery readback |
| stage | importer | write private same-filesystem durable journal/staged files | complete candidate snapshot off target | stage/blob/manifest fsync readback |
| apply | importer | replace/delete only three controlled file surfaces | candidate live snapshot | journal + apply result |
| verify | importer | read controlled files and parse them again | committed or rejected candidate | exact bytes/mode/source/closure readback |
| rollback | importer | reverse durable journal and remove new-only paths | exact pre-import snapshot or explicit recovery failure | rollback/restart readback |
| user integration | template maintainer | review and commit resulting diff | tracked template snapshot updated | commit diff and provenance review |

The importer does not commit, push, open a PR, update a remote, or make a final integration
decision. Those are parent/template-maintainer-only side effects. Descendant users may read the
resulting static files but may not invoke this command as bootstrap behavior.

## Implementation targets and tests

The implementation owner may change only these paths in the Issue #169 implementation slice:

| path | purpose | clauses |
| --- | --- | --- |
| `tools/import_agent_canon_static_seed.py` | command, validation, plan, transaction, rollback, readback | TSSI-001..008, TSSI-010 |
| `tests/tools/test_import_agent_canon_static_seed.py` | bundle, closure, no-op, stale-delete, failure-injection, scope tests | TSSI-001..011 |
| `tests/fixtures/static-seed-c5fa3a22` | repository-owned 36-payload-plus-provenance acceptance fixture | TSSI-002, TSSI-011 |
| `documents/contracts/template-bootstrap.md` | distinguish maintainer import from descendant bootstrap and document command | TSSI-001, TSSI-009 |
| `README.md` | maintainer-only command and source-free boundary | TSSI-001, TSSI-009, TSSI-010 |
| `documents/README.md` | link this design owner | TSSI-010 |

No implementation target may add an AgentCanon checkout, source resolver, runtime importer, updater,
network call, Make target, CI invocation, generated role registry, or second validator. If a target
outside this table is needed, the design is `drifted` and must be revised and re-fingerprinted before
implementation.

### Required test matrix

`tests/tools/test_import_agent_canon_static_seed.py` must use temporary template roots and bundle
fixtures, never a network or AgentCanon checkout. The minimum cases are:

1. valid bundle imports config, provenance, and a role; a new role is added, changed role replaced,
   and absent old role deleted in one plan;
2. same bundle twice returns `pass` then `noop`, with unchanged bytes and mtimes on the second run;
3. invalid provenance keys/version/source/commit, malformed JSON/TOML, malformed old/new manifest
   key closure, wrong mode, missing config, missing role, unreferenced role, wrong same-role path,
   duplicate/unexpected/nested file, root/directory/file symlink (each with its typed finding),
   gitlink-like nonregular object, and executable file all fail before any target digest changes;
4. each five exact case-normalized prefixes and each typed runtime/network/credential marker in
   config, role, and provenance is rejected before destination mutation; ordinary
   `token-efficient`/`token-aware` prose and `tool_output_token_limit` are not rejected by the typed
   scan, while any bytes differing from the reviewed fixture fail `TSSI_BUNDLE_EXPECTED_DIGEST`;
5. target symlink/nonregular/unknown nested entry and absent required target directory are rejected
   without deleting stale roles;
6. injected stage, replace, delete, mode, post-readback, journal cleanup, and process-crash failures restore the
   complete original target path set, bytes, and modes; restart recovery handles each durable state,
   rollback failure is explicit and non-success; committed journal-removal failure retains the
   candidate+journal without rollback and succeeds on committed-only cleanup retry; malformed/multiple
   journals, every manifest schema value/range violation, malformed old/new key closure, expected
   stage/backup path-map mismatch, missing `COMPLETE`, missing `rollback-required`, manifestless
   cleanup tomb, malformed tomb, and noncommitted cleanup tomb recovery fail closed or preserve their
   original failure state; for every legal `preserved_state`, inject crash after tomb durability,
   during entry deletion, after tomb deletion before manifest deletion, during/after manifest deletion,
   and during/after journal directory removal, asserting the state-specific oracle table and that no
   tomb is treated as committed unless `preserved_state=committed` plus candidate readback passes;
   inject the two recognized crash windows (`predeclared` + published stage + no rollback marker and
   `backup_constructing` + published backup + `COMPLETE` + `rollback-required` + no `backed_up`) and
   assert persist-then-cleanup/rollback-only behavior; inject each published-closure/required-marker
   mismatch, predeclared+`backup.partial/`, and extra-marker-only journal and assert
   `TSSI_JOURNAL_MALFORMED` with journal retained;
7. a second concurrent importer immediately fails with `TSSI_CONCURRENT_IMPORT`, exit 75, and
   unchanged target/journal; bundle file replacement, directory symlink swap, exact-entry add/remove,
   and target role/config symlink swap races are rejected or read from stable descriptors without
   changing an uncontrolled path;
8. a spy filesystem/subprocess/network fixture proves no Git, socket, HTTP, environment-secret,
   checkout, source resolver, bootstrap, CI, Docker, or `start_repository.sh` invocation occurs;
9. the command's write-set audit proves that no path outside the three controlled file surfaces and
   documented ephemeral journal changes during a transaction is changed,
   and static role comments preserve path-free schema/digest plus parent-only assignment/authority/
   handback semantics.
10. the test module reads `tests/fixtures/static-seed-c5fa3a22` from its repository-relative source
    path, verifies its c5fa3a22 provenance and exact closure, and passes when launched from an
    unrelated cwd; no developer absolute path or run-local workspace directory is required.

The focused transaction test is an early-fail gate: the implementation handoff runner executes it
first and stops on a nonzero result; `make pr-check` and `make fresh-clone-check` are not allowed to
mask a failed importer oracle or be reported as a substitute for it.

## Validation route and closeout

Implementation validation is ordered as follows:

```bash
python3 -m pytest -q tests/tools/test_import_agent_canon_static_seed.py
make pr-check
make fresh-clone-check
git diff --check
```

The focused test must run first because it owns transaction oracles, and the validation runner stops
on its first failure. `make pr-check` is the single project gate for runtime-independence, docs,
workflow, C++ and focused tests; the route does not repeat those component commands. `make
fresh-clone-check` is a consumer separation proof: it must pass without invoking the importer. Review
readback additionally checks forward coverage (TSSI clause to
implementation/test/doc) and reverse coverage (every changed path, parser field, state transition,
output line, and validation command to a TSSI clause).

## DIC-010 closure locators

- `documents/design/template-static-seed-import.md#Owner、replaceable unit、API` → TSSI-001
- `documents/design/template-static-seed-import.md#Controlled snapshot と side-effect 境界` → TSSI-004, TSSI-009
- `documents/design/template-static-seed-import.md#Bundle の exact closure` → TSSI-002, TSSI-003
- `documents/design/template-static-seed-import.md#Concrete acceptance fixture` → TSSI-011
- `documents/design/template-static-seed-import.md#Prevalidation と deterministic plan` → TSSI-005, TSSI-008
- `documents/design/template-static-seed-import.md#Apply、rollback、readback` → TSSI-006, TSSI-007
- `documents/design/template-static-seed-import.md#State、failure semantics、invariants` → TSSI-001..010
- `documents/design/template-static-seed-import.md#Implementation targets and tests` → target/path closure
- `documents/contracts/template-bootstrap.md#State handling` → descendant no-mutation boundary
- `tools/check_runtime_independence.py#validate_static_seed` → current post-import closure consumer
- AgentCanon `documents/contracts/static-seed-export.md#出力`, `#Source-free Consumer Validation`,
  and `documents/design/static-seed-consumer-static-projection.md#Export/checker gates` at
  `c5fa3a22c8486952dc6dede0cc3a25e5ba7741e5` → producer and semantic-prefix evidence

The design is complete only when the importer, tests, documentation, and validation route all
read back these locators. A changed owner, write set, transaction invariant, semantic prefix set,
or command surface is design drift, not an implementation shortcut.
