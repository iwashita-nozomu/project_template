<!--
@dependency-start
contract evidence
responsibility Records owner-bounded defer decisions that are outside the parent projection worker scope.
upstream design ../../vendor/agent-canon/documents/parent-repository-audit/README.md static-first validation and owner boundary
upstream design ../../vendor/agent-canon/documents/parent-repository-audit/audit-unit/environment-containers.md environment owner and runtime boundary
upstream implementation ../../vendor/agent-canon/tools/agent_tools/dependency_module_change.py managed clone lifecycle
downstream design ../../AGENTS.md parent orchestration and worker trust boundary
@dependency-end
-->

# Parent Audit Projection Defer Receipts

## Reader Map

- owner、対象、理由、実行しなかった操作、次の action の順に読む
- 本文書は親固有の defer evidence であり、canonical audit unit の invariant を上書きしない
- defer は pass の代替ではなく、projection の責務外または owner が進行中であることを明示する

## Receipts

### environment-containers

- owner: `environment-maintenance`
- project-review findings: `R4`, `R6`
- scope: `docker/**`, `.devcontainer/**`, host mount、cold-build、runtime environment
- status: `deferred-owner-in-progress`
- reason: 今回は AgentCanon pin、root view readback、親 reader route、audit evidence の projection
  だけを変更し、Docker/devcontainer の source diff はない。Docker image 間の差分 build は
  canonical audit policy の対象外であり、cold image/runtime の実測を未実行のまま pass としない。
- evidence: `git diff --name-only origin/main -- docker .devcontainer CONTAINER_OPERATIONS.md agent-canon-environment.toml` は空
- additional finding: full-tree dependency review detected missing dependency manifests in
  `.devcontainer/parent-environment.toml` and `.devcontainer/post-create-parent.sh`; these are
  environment owner files and are deferred with the same owner boundary rather than edited in the
  pin/reader projection.
- next action: `environment-maintenance` が必要と判断したとき、変更された configuration の
  static validator と runtime-only invariant の最小 command を owner packet に従って実行する。

### workspace-clone-lifecycle

- owner: `dependency-module-change` / `worktree-health`
- scope: `/mnt/l/workspace/project_template/workspace/parent-audit-projection/project_template`
  と対応する AgentCanon source clone
- status: `deferred-until-parent-integration`
- reason: ユーザー指定の fresh parent clone と source clone は branch/PR readback のため保持する。
  worker は他の checkout を削除せず、既存 dirty checkout にも戻らない。
- evidence: parent branch `codex/parent-audit-projection`、AgentCanon accepted pin `681a5929`、両 clone の
  explicit path を確認済み
- next action: parent integrator が PR review/merge を終えた後に canonical cleanup route を選択する。

### runtime-log

- owner: `runtime-log-repair`
- scope: runtime dashboard/log archive、未選択の実行 profile
- status: `accepted-source-projected-with-owner-followup`
- reason: accepted AgentCanon source `681a5929b14c845c61153f2293c8d1001450500a` に含まれる
  runtime-log archive contract/tool を parent submodule pin と root-view readback とともに一度で投影した。
  archive mount/外部 log repository への publish は親 projection の必要条件ではないため実行しない。
- evidence: `runtime_log_archive_git.py --help`、default `check-hook-hot-path` pass、source targeted
  test は `47 passed, 2 failed, 34 subtests passed`。失敗は source main 上の reverse-correspondence
  branch-context mismatch と `publication_attempt_lock_invalid` oracle mismatch であり、親側で修正しない。
- next action: runtime-log owner が source test failure の原因を判断し、必要なら source PR/accepted
  follow-up で修正する。archive mount が選択された workflow のときだけ owner route を実行する。

### pull-request-lifecycle

- owner: parent integrator / `pr-processing`
- scope: GitHub PR create、review、merge、close
- status: `deferred-parent-only`
- reason: worker は commit/push までを担当し、PR の create/merge/close と最終 integration decision
  は parent-only trust boundary である。
- evidence: topic branch の push receipt は closeout で返し、PR URL は parent integrator が作成後に追記する
- next action: push 済み exact head から通常の parent PR を作成し、CI/review/merge を行う。

### accepted-source-shim-materialization

- owner: AgentCanon source `agent-canon-update` / skill materializer owner
- scope: vendored `.agents/skills/agent-log-analysis/SKILL.md` generated shim
- status: `deferred-source-follow-up`
- reason: accepted source main `681a5929b14c845c61153f2293c8d1001450500a` の canonical skill と
  committed materialization record に digest drift があり、既存 `materialize --all` が
  `content_delta=1` を返した。second `readback --all` は pass だが、parent projection で
  submodule 内部を新規 commit する権限・scopeはない。
- evidence: changed path は `.agents/skills/agent-log-analysis/SKILL.md` の materialization record
  だけ。parent gitlink は accepted SHA に固定し、source worktree を clean に readback した。
- next action: AgentCanon source owner が materialize output を source PR として commit/pushし、
  accepted main と generated shim の固定点を再発行する。parent pin はその accepted SHA の
  次回 projection で更新する。
