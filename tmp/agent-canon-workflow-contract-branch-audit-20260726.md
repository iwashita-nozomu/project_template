<!--
@dependency-start
contract report-artifact
responsibility Records a task-local audit of AgentCanon workflow branches and proposed normalization without becoming policy; this report remains task-local and noncanonical.
upstream design ../vendor/agent-canon/agents/canonical/CODEX_WORKFLOW.md workflow classification and task boundary source
upstream design ../vendor/agent-canon/agents/canonical/CODEX_SUBAGENTS.md subagent inventory, capacity, and lifecycle source
upstream design ../vendor/agent-canon/agents/canonical/CLI_ENTRYPOINTS.md CLI and runtime entrypoint source
upstream design ../vendor/agent-canon/agents/TASK_WORKFLOWS.md workflow family reader-path source
upstream design ../vendor/agent-canon/agents/task_catalog.yaml workflow family and role registry source
upstream design ../vendor/agent-canon/agents/workflows/codex-goals-workflow.md goals surface source
upstream design ../vendor/agent-canon/agents/workflows/experiment-workflow.md experiment runner and artifact source
upstream design ../vendor/agent-canon/agents/workflows/implementation-waterfall-workflow.md implementation and validation gate source
upstream design ../vendor/agent-canon/agents/workflows/research-workflow.md research decision-loop source
upstream design ../vendor/agent-canon/agents/workflows/agent-canon-pr-workflow.md publication lifecycle source
upstream design ./agent-canon-workflow-contract-branch-audit-20260726.raw.json sibling raw evidence artifact
@dependency-end
-->

# AgentCanon workflow 契約分岐監査（2026-07-26）

この文書は、AgentCanon の指定 workflow 正本を読み取り専用で監査し、契約として固定すべき分岐と、失敗意味論・安全性のために維持すべき動的分岐を分けた提案レポートです。正本の修正や policy の変更ではありません。

読み方の橋渡し: 以下の概要で件数と主張を把握し、判定基準を確認してから全所見表で観測・推論と根拠を追跡してください。

## 概要

12 件を確認しました。P0 は workflow family 集合の不一致（F1）と mini/medium registry の漏れ（F2）の 2 件、P1 は 6 件、P2 は 4 件です。主な提案は、環境依存 backend を adapter 境界へ閉じ、logical state と同一の確認 record を CLI、run bundle、closeout に投影することです。既存の typed failure、安全性、研究レビューの decision loop は動的分岐として保持します。

この件数と提案の根拠は、機械可読の生証跡と読者向けの全所見表に分けて、次の2ファイルへ保存しています。

- 生証跡: `tmp/agent-canon-workflow-contract-branch-audit-20260726.raw.json`
- 読者向け表: `tmp/agent-canon-workflow-contract-branch-audit-20260726.md`

## 判定基準/読み方

- **観測** は指定正本の現在の記述、**推論** はそこから導く契約上の残差です。
- `P0` は closed set の不一致が route を変えるもの、`P1` は環境/backend が確認経路へ漏れるもの、`P2` は既存 typed contract の projection 残差です。
- `shared_skill_or_workflow_gap` は共通 adapter/skill/workflow 契約の候補、`review_required` は既存契約が部分的に成立しており実装前の追加 review が必要な候補です。
- 表の「固定すべき契約（推論）」は設計提案であり、現在存在する API 名の主張ではありません。

## 全所見表

| 優先度 | ID | 種別 | 現在の分岐（観測） | 固定すべき契約（推論） | 環境差を閉じ込める境界 | ユーザー確認動線 | 根拠 | 確度/反証 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P0 | F1 | `contract_set_drift` / shared gap | **観測:** CODEX_WORKFLOW は 6 family、TASK_WORKFLOWS/task_catalog は owner-bounded を含む 7 family。<br>**推論:** 入口により family と次 gate が変わる。 | catalog を closed family-set 正本にし、`workflow_id`、理由、次 gate、確認の同一 schema を投影する。 | WorkflowFamilyAdapter（catalog→reader/task packet）。 | family、理由、次 gate、確認要否を一度提示し、分類失敗は確認待ちにする。 | `CODEX_WORKFLOW.md:L363-L383`<br>`TASK_WORKFLOWS.md:L93-L103`<br>`task_catalog.yaml:L169-L175` | 高 / summary-only との反証はあるが route を変えるため残る。 |
| P0 | F2 | `registry_contract_leak` / shared gap | **観測:** task prose は mini を bounded exploration/execution にも置くが、CODEX_SUBAGENTS は mini/medium を T14 `skill_evaluator` に限定。<br>**推論:** mini scope が registry より広く読める。 | closed model/profile registry を唯一の契約にし、role、agent type、profile、activation reason を共通化する。 | ModelProfileAdapter（closed registry→catalog/reader projection）。 | role/model と mini 制限を一つの確認行にし、profile mismatch は fallback しない。 | `task_catalog.yaml:L210-L220`<br>`CODEX_SUBAGENTS.md:L711-L721`<br>`task_catalog.yaml:L538-L567,L698-L702` | 高 / 候補 prose との反証はあるが prompt に漏れる。 |
| P1 | F3 | `user_confirmation_normalization` / shared gap | **観測:** `/agent` がある runtime と TOML 直接参照の runtime で inventory 入口が別。<br>**推論:** backend 可用性が role 確認形式へ漏れる。 | SubagentInventoryAdapter の共通 `role_id/agent_type/availability/freshness/reason` schema。 | `/agent`/TOML backend を adapter 内に閉じる。 | source、状態、候補、次 action を同じ日本語 record で提示する。 | `CLI_ENTRYPOINTS.md:L46-L57`<br>`CODEX_SUBAGENTS.md:L524-L535` | 高 / 手順差だけとの反証はあるが action を変える。 |
| P1 | F4 | `user_confirmation_normalization` / shared gap | **観測:** goals feature、goal.md、session UI、goal_loop の有無・mirror・confirmation で branch。<br>**推論:** durable/session/mechanical state の不一致時に確認責務が分かれる。 | GoalSurfaceAdapter が parse/draft→共通 ConfirmationRecord→mirror/status gate を行う。 | UI、goal_loop、goal.md の差を adapter 内へ閉じる。 | draft→同一 record→mirror/queue→plan/status→implementation gate。 | `CODEX_WORKFLOW.md:L242-L262`<br>`codex-goals-workflow.md:L27-L43,L68-L100,L149-L175` | 高 / 既に goal.md 正本という反証はあるが envelope が未統一。 |
| P1 | F5 | `environment_normalization` / shared gap | **観測:** managed runner/artifact envelope は main server host に明示され、local/verified runner は入口が分かれる。<br>**推論:** provenance の最低集合と close 判断が backend に漏れる。 | FormalRunAdapter が backend 非依存の command/environment/source/config/run/eval/artifact/log 最小集合を保証する。 | local/managed/host/admission 差を adapter 内へ閉じる。 | 開始時に backend/artifact plan、終了時に manifest readback と rerun/追加検証/close を同形式で確認する。 | `experiment-workflow.md:L89-L96,L182-L230,L297-L320` | 中高 / main-host formal 限定なら意図的だが、formal 相当の境界は review が必要。 |
| P1 | F6 | `user_confirmation_normalization` / shared gap | **観測:** implementer は worker 既定、spark は bounded 選択、experimenter は runner 既定で worker は scoped output。<br>**推論:** logical role より物理 agent/backend が handoff を決める。 | Logical ImplementerRole と共通 HandoffRecord（owner、authority、backend、review、validation、確認）。 | agent type/backend を HandoffAdapter 内に閉じる。 | logical role、実 backend、write scope、review、blocked 理由を一度提示し、変更時は同じ record を改訂する。 | `CODEX_SUBAGENTS.md:L537-L555,L698-L721`<br>`CLI_ENTRYPOINTS.md:L101-L108` | 高 / blocked evidence は既存だが logical envelope は残差。 |
| P1 | F7 | `user_confirmation_normalization` / shared gap | **観測:** conversation、GitHub-only read、local read/edit/validation/mutation は別 boundary。<br>**推論:** mutation 入口で authority と確認を同じ machine transition に束ねていない。 | `TaskBoundary` を typed transition とし、mutation への全遷移で同じ authority/confirmation record を要求する。 | GitHub/local/CLI mutation adapter。 | 遷移ごとに日本語 update→path/action→authority→確認待ち/次 gate。 | `CODEX_WORKFLOW.md:L179-L190,L91-L102` | 高 / user update 規則は既存だが machine record がない。 |
| P1 | F8 | `evidence_projection_normalization` / review required | **観測:** spawn authorization、capacity handshake、`SUBAGENT_AUTHORIZATION=required` は部分的に存在。<br>**推論:** runtime、goal、waterfall で payload/key が分散する。 | SpawnAuthorizationAdapter と共通 record（requested/authorized/capacity/payload/next gate/確認）。 | runtime policy、capacity、handoff の差を adapter 内へ閉じる。 | authorized/granted→spawn。required/pending_user→同じ確認 recordで待機。capacity_blocked/queued→capacity理由のときだけqueue。denied→fail-closedでescalation/revised authority。stale_packet→再生成/readback後に確認。 | `CODEX_SUBAGENTS.md:L105-L126`<br>`implementation-waterfall-workflow.md:L205-L226` | 高 / 既存 typed rule があるため review_required。 |
| P2 | F9 | `evidence_projection_normalization` / review required | **観測:** `missing_file_triage` が template/canon/root-view 確認後の分類・次 action を保持。<br>**推論:** owner/path/action/authority/確認の envelope が caller 間で不統一。 | MissingPathAdapter の共通 record。既存 disposition は typed のまま投影する。 | template/canon/root-view/task-local の確認を adapter 内へ閉じる。 | 分類と create/sync/保留 action を一度提示し、破壊的 action は既存 gate へ接続。 | `CODEX_WORKFLOW.md:L166-L177` | 中 / triage で十分という反証があるため review に限定。 |
| P2 | F10 | `evidence_projection_normalization` / review required | **観測:** semantic handoff を優先し、必要時だけ run bundle を materialize。<br>**推論:** bundle は storage projection なのに close predicate と同一 envelope でない。 | LifecycleSemanticAdapter が semantic completion envelope を持ち、bundle は storage projection とする。 | handoff/tool result と run-bundle files の差を adapter 内へ閉じる。 | 開始/closeout で同じ envelope を readback し、bundle の有無を確認経路から隠す。 | `CODEX_WORKFLOW.md:L253-L262`<br>`implementation-waterfall-workflow.md:L205-L216`<br>`CODEX_SUBAGENTS.md:L524-L535` | 中 / Decision Sufficiency が部分充足するため残差のみ。 |
| P2 | F11 | `environment_normalization` / shared gap | **観測:** host Docker check は「必要なら」。<br>**推論:** capability により実行/skip/理由の user flow が分かれる。 | DockerValidationAdapter の一つの entrypoint/readback。capability は typed skip reason を返す。 | host Docker capability と inner checks の差を adapter 内へ閉じる。 | capability probe→実行/skip 理由→同じ日本語 validation table。 | `implementation-waterfall-workflow.md:L844-L850` | 中 / 任意条件は正当だが共通 record が不足。 |
| P2 | F12 | `evidence_projection_normalization` / review required | **観測:** capacity 用語、queue、restart_required、reservation lifecycle は既に typed。<br>**推論:** handshake/config/workflow/user status の projection が同一かは未確認。 | CapacityStatusAdapter の共通 status（requested/effective/queue/blocked/granted/capacity_event_kind/next action/確認）。 | config、platform handshake、workflow demand、reservation の差を adapter 内へ閉じる。 | granted→proceed。queued→capacity理由のときだけqueue。restart_required→restart/readback gate。reservation_leak/missing_descendant/missing_handback→closeout fail-closedとrepair。model_capacity_eventはthread_saturationと別表示。 | `CODEX_SUBAGENTS.md:L105-L126,L791-L802` | 中 / Capacity contract は既存のため review_required。 |

## 契約化済み/正当な動的分岐として除外したもの

次は環境依存の確認経路ではなく、安全性・失敗意味論・研究判断を担うため、所見には数えていません。

| 動的分岐 | 除外理由 | 根拠 |
| --- | --- | --- |
| research review decision (`report_rewrite_required` 等) | evidence に応じて loop を戻す正本 state machine。 | `research-workflow.md:L56-L84` |
| `SkipController` 起動前 skip | case/resource predicate に基づく実験挙動。 | `experiment-workflow.md:L182-L196` |
| running writer timeout の `preserve_running_instance` | write safety と lifecycle integrity を守る typed state。 | `CODEX_SUBAGENTS.md:L135` |
| branch reuse/collision/protected state | checkout preservation と explicit authority の安全境界。 | `CODEX_WORKFLOW.md:L91-L102` |
| append-only PR lifecycle | rebind/freeze/review/CAS/merge/readback の publication state machine。 | `agent-canon-pr-workflow.md:L54-L93` |
| adaptive backlog loop | review decision に応じて次 iteration/pass へ戻す outer loop。 | `research-workflow.md:L71-L84` |
| validation failure taxonomy | contract、観測層、原因、意図を保持して修復先を選ぶ。 | `implementation-waterfall-workflow.md:L673-L679` |
| experiment isolation predicate | main を既定とし、長時間/破壊的試行だけ隔離する安全条件。 | `research-workflow.md:L156-L161` |
| freshness status + 4-field mutation gate | clean/deferred/dirty/diverged と authority/reason の既存共通安全契約。 | `CODEX_WORKFLOW.md:L69-L102` |

## 制約

- 指定された AgentCanon workflow slices と、Markdown 規約の 2 文書だけを read-only で確認しました。未指定の実装、reports、experiments、notes、documents は監査していません。
- `F1`〜`F12` の adapter 名はすべて設計提案です。既存 API の存在を主張しません。
- `./tmp` はユーザー指定の task-local 出力であり、正本、root view、AgentCanon source ではありません。既存 dirty state は変更していません。
- 環境依存分岐そのものを消すのではなく、typed state を保持したまま adapter 境界と共通確認 record へ投影する方針です。

### Prose graph residual classification

最終 prose graph 診断で残った次の claim は、表セルと境界文を機械 parser が支持辺へ投影できなかったことによる `tool-false-positive` と分類します。診断結果は claim の弱化・削除を許可しません。

| claim | 分類 | 理由 / 根拠 | 処置 |
| --- | --- | --- | --- |
| claim:3 | `tool-false-positive` | **観測:** 「adapter 名は設計提案であり、既存 API の存在を主張しない」は明示的な境界・非目的文です。 | 非目的境界として保持し、unsupported claim として削除しません。 |
| claim:6 | `tool-false-positive` | **観測:** F10 表行に `CODEX_WORKFLOW.md:L253-L262`、`implementation-waterfall-workflow.md:L205-L216`、`CODEX_SUBAGENTS.md:L524-L535` の根拠があり、raw JSON の F10 `source_refs` に同じ根拠があります。 | parser の supports edge 欠落として記録し、F10 の主張と根拠を保持します。 |
| claim:7 | `tool-false-positive` | **観測:** F11 表行に `implementation-waterfall-workflow.md:L844-L850` の根拠があり、raw JSON の F11 `source_refs` に同じ根拠があります。 | parser の supports edge 欠落として記録し、F11 の主張と根拠を保持します。 |

## 次のアクション

1. P0 の family set と model/profile registry projection を owning source で adjudicate する。
2. P1 の F3〜F8 について、共通 ConfirmationRecord と各 adapter の owner/API shape を design review で固定する。
3. P2 は既存 typed contract の readback checker が不足する箇所だけを review backlog に登録する。
4. 実装前に、ユーザー確認 record が CLI、非 UI runtime、managed/local backend、queue/blocked state で同型になる fixture を決める。

## Source Packet / Artifact Manifest / quality checklist

### Source Packet

- `vendor/agent-canon/agents/canonical/CODEX_WORKFLOW.md`
- `vendor/agent-canon/agents/canonical/CODEX_SUBAGENTS.md`
- `vendor/agent-canon/agents/canonical/CLI_ENTRYPOINTS.md`
- `vendor/agent-canon/agents/TASK_WORKFLOWS.md`
- `vendor/agent-canon/agents/task_catalog.yaml`
- `vendor/agent-canon/agents/workflows/codex-goals-workflow.md`
- `vendor/agent-canon/agents/workflows/experiment-workflow.md`
- `vendor/agent-canon/agents/workflows/implementation-waterfall-workflow.md`
- `vendor/agent-canon/agents/workflows/research-workflow.md`
- `vendor/agent-canon/agents/workflows/agent-canon-pr-workflow.md`

### Artifact Manifest

| artifact | 用途 | 状態 |
| --- | --- | --- |
| `tmp/agent-canon-workflow-contract-branch-audit-20260726.raw.json` | 完全な機械可読 finding と除外分岐 | 作成済み |
| `tmp/agent-canon-workflow-contract-branch-audit-20260726.md` | JSON から導出した日本語 reader report | 作成済み |

### Quality checklist

- [x] 生 JSON の schema、metadata、12 finding、9 rejected dynamic branches を含めた。
- [x] Markdown 表は全 12 finding を省略せず、観測と推論を明示した。
- [x] 各 finding に priority、category、classification、source refs、typed state、user flow、反証、owner を記録した。
- [x] adapter 名を提案として扱い、typed failure と安全性の動的分岐を除外した。
- [x] `python3 -m json.tool` は exit 0 で完了した。
- [x] `tools/bin/agent-canon docs check tmp/agent-canon-workflow-contract-branch-audit-20260726.md` は `DOCS_CHECK=pass` で完了した。
- [x] prose graph 診断 status: reviewed。claim:3/6/7 は `tool-false-positive` と分類し、主張を保持した。概要→成果物一覧の橋渡し文を追加した。

`document_split_decision=split:raw JSON と reader report は source evidence と解釈の異なる consumer を持つため分離`。
