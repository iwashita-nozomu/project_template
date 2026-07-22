<!--
@dependency-start
contract design
responsibility Defines the canonical r9 experiment README metadata contract and its rationale.
upstream design ../AGENTS.md repository scope, ownership, design-integrity, and documentation contract.
upstream design ../vendor/agent-canon/documents/dependency-manifest-design.md dependency-header contract.
upstream design ../vendor/agent-canon/documents/SHARED_RUNTIME_SURFACES.md shared document ownership policy.
downstream implementation ./experiment-readme-contract-r9.json normative schema lookup authority.
downstream design ../README.md project documentation entrypoint.
@dependency-end
-->

# Experiment README contract — r9 canonical design

Status: normative design packet for the future implementation. This file and
`experiment-readme-contract-r9.json` is the sole lookup authority; the Markdown is rationale for
the contract. `document-flow-review-r2.md`, `document-flow-review.md`,
`design-review.md`, and earlier packet prose are historical evidence only.

No AgentCanon source is edited by this audit. No implementation tests are
created. The contract continues to reject word count, character count, section
length, heading count, line count, and OOP scores as completeness signals.

## 1. Exact metadata block and schema

Every README has exactly one contiguous block whose opening line is:

```text
<!-- experiment-readme-contract
```

The payload is one JSON object, followed by a line containing `-->`. The object
must validate against `experiment-readme-contract-r9.json`. There is no YAML
front matter, alternate comment marker, or second metadata block.

The exact required top-level fields are:

| Field | Type | Required rule |
| --- | --- | --- |
| `schema_version` | string | Exact value `experiment-readme-contract/v1`. |
| `contract_revision` | string | Exact value `r9`. |
| `readme_kind` | enum string | One of `plan`, `run`, `result`, `report`. |
| `status` | enum string | One of `draft`, `planned`, `running`, `complete`, `failed`, `partial`, `superseded`; the matrix restricts combinations. |
| `reader_question_id` | enum string | One of `approve_protocol`, `identify_execution`, `locate_evidence`, `interpret_bound_run`; must equal the matrix value. |
| `reader_question` | non-empty string | Human rendering of the selected reader question. |
| `topic` | identifier string | Topic identity. |
| `run_name` | identifier string or null | Null for a plan without a concrete run; actual run identity for run/result/report runtime modes. |
| `slots` | array of slot objects | Contains all 13 stable slot IDs exactly once. |
| `bindings` | object | Contains `registry` and `topic_readme`; other keys are declared in the JSON schema and required by the selected matrix row. |

Every object in the block has `additionalProperties=false`. Unknown keys are a
contract error (`ERD-013`), including unknown keys nested in evidence,
references, bindings, digests, and slots. Duplicate slot IDs are an error
(`ERD-003`). Zero metadata blocks is `ERD-001`; more than one is
`ERD-014`.

The schema deliberately contains no `ordered_structure`, heading list, prose
length, line-count, or OOP field. A README may display slots in any order.

## 2. Stable slots and field-level evidence binding

The checker reads the `x_slot_contract` and `x_reader_dependency_graph` fields
from the JSON file; this Markdown repeats their meaning for implementation
review but is not a second lookup table.

| Slot | Required semantic evidence | Exact runtime/source bindings |
| --- | --- | --- |
| `EXP-README-01` objective/decision | `prose_claim`; decision and non-goal are visible at the declared anchor | `registry` and `topic_readme` when present. |
| `EXP-README-02` hypotheses/claims | `prose_claim` plus `oracle_ref`; each claim names direction or bounded descriptive scope | Plan/report prose; no runtime file substitutes for the claim. |
| `EXP-README-03` method/algorithm contract | `prose_claim`, `source_ref`, `entrypoint_ref`; source map names file/function and state/acceptance boundary | `entrypoint`, `source_snapshot`, and runtime `run_manifest`. |
| `EXP-README-04` variables/controls | `prose_claim`, `config_ref`; controls include baseline/seed/timeout/dtype or explicit not-applicable state | `config` and `config_source`; compare declared config identity. |
| `EXP-README-05` datasets/inputs | `prose_claim`, `config_ref`; source/version/split/schema or explicit planned input | `config`, `source_snapshot`, and `artifact_manifest` where packaged inputs are artifacts. |
| `EXP-README-06` environment/resources/GPU allocation | `prose_claim`, `environment_ref`, `resource_ref`, `gpu_allocation_ref`; caller/scheduler ownership is explicit | `environment`, `resource_plan`, and `gpu_allocation`; these are separate predicates, not matrix prerequisites. |
| `EXP-README-07` run matrix | `prose_claim`, `matrix_ref`; rows name factors, variants, controls, inputs, and acceptance/stop state | `config` and actual case/run records via `run_manifest`; no edge from resource allocation back into matrix construction. |
| `EXP-README-08` command/entrypoint | `command_ref`, `entrypoint_ref`, `registry_ref`, `config_ref` | `registry`, `command`, `entrypoint`, `config`, and `run_manifest`; exact normalized argv equality. |
| `EXP-README-09` outputs/artifact identity | `artifact_ref`; every promised/observed artifact has path and manifest identity | `artifact_manifest` and `run_manifest`. |
| `EXP-README-10` failure semantics | `prose_claim`, `terminal_ref`; success/failure/timeout/partial meanings are explicit | `terminal`; `partial` is also required for partial status. |
| `EXP-README-11` analysis/oracles/exclusion criteria | `oracle_ref`, `exclusion_ref`; denominator/directionality and excluded cases are explicit | `terminal` and `artifact_manifest`; no result claim without the oracle. |
| `EXP-README-12` reproducibility | `replay_ref`, `command_ref`, `config_ref`, `source_ref` | `run_manifest`, `command`, `config`, `config_source`, `source_snapshot`, `environment`, and `artifact_manifest`. |
| `EXP-README-13` status/results links | `status_ref`; status transition and result/report/replacement link are exact | `registry`, `result_readme`, and `report`; runtime modes also bind `run_manifest`. |

### Binding object and optional digest semantics

Each binding is an object with required relative `path`, optional JSON Pointer
`json_pointer`, optional `dirty_state=clean|dirty|unknown`, optional
`dirty_policy=reject|allow_with_digest|allowed_planned`, and optional
`optional_digest` containing exactly `algorithm=sha256`, a lowercase
64-hex `value`, and `source=declared|observed`.
Evidence references select a binding with `reference.binding_key` and may select
a JSON pointer.

An absent or null digest means “path/key equality only”; it is not a claim that
the object is reproducible. A present digest must equal the observed SHA-256 at
every bound source that supplies that object. Planned rows may use
`dirty_policy=allowed_planned`; runtime dirty sources require
`dirty_policy=allow_with_digest`, `dirty_state=dirty`, and a matching
observed digest. A required reproducibility slot must include `digest_ref`
evidence when the selected mode requires observed digests.

The exact ExperimentRunner mapping is:

| README metadata | Manifest/file key | Equality or predicate |
| --- | --- | --- |
| `topic`, `run_name` | `run_manifest.json:/topic`, `/run_name`; `config.json:/topic`, `/run_name`; all artifact manifests | Exact identifier equality. |
| `EXP-README-08` command | `command.json` command/source/match; `run_manifest.json` command fields; registry command | Exact decoded command-string equality across the registry, entrypoint/config declaration, and run manifest; no token reordering or path rewriting is permitted. |
| `EXP-README-08` config | `config.json`, `config_source.yaml`, registry config path | Relative path equality; digest equality when declared. |
| `EXP-README-03` source map | `source_snapshot.json:/files`, `/command_source_files`, `/git`; source snapshot records | Relative source paths and commit/tree/dirty state bind the named code. |
| `EXP-README-06` environment | `environment.json` and resource certificate/readback | `cwd`, argv, environment key/value policy, runtime identity, and declared owner match; secrets use the existing redacted witness, not README prose. |
| `EXP-README-06` resources | `resource_plan` binding to `execution_resource_plan.json` or its persisted witness | Plan fingerprint, owner, resource request, state, and readback witness match. |
| `EXP-README-06` GPU | `gpu_allocation` binding to allocation/certificate/readback witness | Allocation provenance, visible IDs, reservation/readback, and plan fingerprint match. |
| `EXP-README-10` terminal | `terminal_evidence.json` fields `schema_version=terminal-evidence/v1`, `terminal_event_id`, `status`, `terminal_timestamp`, `failure_code`, `failure_stage`, `topic`, `run_name`, `run_manifest_relative_path`, and `provenance` | Terminal evidence exists and is compatible with the declared status. |
| `EXP-README-10`/`11` partial | `partial_evidence.json` fields `schema_version=partial-evidence/v1`, `terminal_event_id`, `status=partial`, `terminal_timestamp`, `partial_is_completion=false`, `stop_reason`, `partition`, `topic`, `run_name`, `run_manifest_relative_path`, and `provenance` | The four-way completed/failed/in-flight/unstarted partition agrees with README exclusions. |
| `EXP-README-09` outputs | `artifact_manifest.json:/artifacts`, `/result_dir`, `/artifact_count` | Every README artifact path is present; recorded size and digest compare exactly. |
| `EXP-README-13` status | `run_manifest.json:/status`, `exit_code`, `finished_at_utc`; result/report links | Status and replacement/result/report identity agree. |

### Dirty and partial predicates

For runtime rows, `source_snapshot.json:/git/dirty` must be false, or the
README must include `dirty_state=dirty`, `dirty_policy=allow_with_digest`,
and per-file observed digests. Unknown dirty state emits `ERD-010`; a policy
never waives a digest mismatch. Planned rows may explicitly classify dirty or
unknown source as planned evidence.

`partial` requires `terminal` and `partial` bindings, the typed partition and
stop reason, and `partial_is_completion=false`. It cannot claim full matrix
coverage or verified reproducibility. `failed` requires terminal failure kind
and log identity. `superseded` requires a replacement `replacement_link` whose pointer direction is
`forward_required`. `forward_references=false` still forbids ordinary future
runtime claims; the replacement pointer is the one named exception for
`plan:superseded`, `run:superseded`, `result:superseded`, and
`report:superseded`.

## 3. Normative kind/status matrix

The complete matrix is encoded in `x_kind_status_matrix` in the JSON file. It
has one object for every allowed pair; all 13 slots are required. The
`plan:complete` row has boolean `observed_result_claims=false`,
`observed_claim_predicate_id=R5.CLAIM.NO_OBSERVED`, and the direct predicate
object `observed_claims=R5.CLAIM.NO_OBSERVED`. Each row
contains direct terminal, log, partial-partition, replacement, dirty-source,
Runner-status, observed-claim, forward-reference, runtime, and stable
predicate-ID fields. The following
is a navigation rendering of that exact JSON, not a second authority:

| Kind | Allowed status | Reader question | Forward refs | Runtime required | Observed results |
| --- | --- | --- | --- | --- | --- |
| plan | draft | approve protocol | yes | no | no |
| plan | planned | approve protocol | yes | no | no |
| plan | complete | approve protocol | no ordinary refs | no | no |
| plan | superseded | approve protocol | no ordinary refs; replacement pointer forward | no | no |
| run | running | identify execution | no | yes | no |
| run | complete | identify execution | no | yes | yes |
| run | failed | identify execution | no | yes | no |
| run | partial | identify execution | no | yes | no |
| run | superseded | identify execution | no ordinary refs; replacement pointer forward | yes | no |
| result | running | locate evidence | no | yes | no |
| result | complete | locate evidence | no | yes | yes |
| result | failed | locate evidence | no | yes | no |
| result | partial | locate evidence | no | yes | no |
| result | superseded | locate evidence | no ordinary refs; replacement pointer forward | yes | no |
| report | draft | interpret bound run | yes, planned references only | no | no |
| report | complete | interpret bound run | no | yes | yes |
| report | failed | interpret bound run | no | yes | no |
| report | partial | interpret bound run | no | yes | no |
| report | superseded | interpret bound run | no ordinary refs; replacement pointer forward | yes | no |

Every other kind/status pair is invalid and returns `ERD-012`. `report:draft`
explicitly permits planned references, but those references cannot satisfy an
observed runtime slot. `plan` statuses never claim observed results.

## 4. Acyclic reader graph and separate resource predicates

The reader dependency graph is the JSON edge list:

```text
01 -> 02 -> 03 -> 04 -> 05 -> 07 -> 08 -> 09 -> 10 -> 11 -> 12 -> 13
                 |       \-> 06
                 \-----------------------> 12
```

`EXP-README-06` is established from method/input requirements and caller
ownership independently of `EXP-README-07`. Resource evidence may annotate a
matrix row with a resource class, but the matrix does not construct the
environment/resource/GPU predicate and resource allocation does not become a
reader prerequisite for defining the matrix. There is no environment ↔ matrix
edge.

The separate predicates are: `environment_declared`, `resource_feasible`,
`gpu_allocation_observed`, `matrix_declared`, and `matrix_case_covered`.
ExperimentRunner/resource owners establish runtime predicates; the README
checker verifies only the declared binding and equality.

## 5. Checker API, CLI, JSON result, and errors

The sole semantic owner is `tools/ci/check_experiment_readme.py`. Its public API
is:

```python
ReadmeCheckResult check_readme(
    readme_path: Path,
    *,
    repo_root: Path,
    kind: str | None = None,
    status: str | None = None,
    registry_path: Path | None = None,
    run_dir: Path | None = None,
    schema_path: Path | None = None,
    require_runtime: bool = False,
) -> ReadmeCheckResult
```

The CLI is:

```text
python3 tools/ci/check_experiment_readme.py --repo-root ROOT --path README [--kind KIND] [--status STATUS] [--registry REGISTRY] [--run-dir RUN_DIR] [--schema SCHEMA] [--require-runtime] [--json]
```

`--kind` and `--status` are independently optional. An omitted value is
inferred only from the exactly-one metadata object. A supplied value must equal
the metadata value; otherwise the checker emits `ERD-020`. No value is
inferred from headings, filename, path, registry, run manifest, or prose.
Missing metadata needed for inference is `ERD-022`; zero or duplicate blocks
remain `ERD-001` and `ERD-014`.

When `--schema` is omitted, the checker loads exactly
`<repo-root>/documents/experiment-readme-contract-r9.json`. If supplied, the
resolved path must be exactly that path; every alternate schema path emits
`ERD-021` and exits 2. The packet-local JSON has the same basename for audit
validation only and is not a worker CLI schema alternate.

`--path` is resolved relative to `--repo-root`; absolute paths must remain
inside that root. Relative binding paths use `--run-dir` when supplied and
otherwise the README's directory. Registry paths use `--repo-root`. The
checker invokes `check_experiment_registry.py` exactly once when registry
delegation is selected, propagates a malformed/nonzero/exceptional delegation
as `ERD-015`, and never copies registry predicates.

The JSON output is exactly one `ReadmeCheckResult` object with required keys
`schema_version`, `passed`, `readme_kind`, `status`,
`reader_question_id`, `slot_results`, `bindings`, and `findings`.
`slot_results` is one record per stable slot; `bindings` reports resolution,
JSON pointer, digest, equality, and runtime-required state; `findings` carries
the stable error code, severity, path, slot IDs, evidence IDs, and message.
`--json` emits only this object; human mode preserves the same object and
writes presentation to stderr.

Exit precedence is exact: 2 (usage, schema, path, metadata, unknown key,
argument/metadata mismatch, noncanonical schema, or registry delegation), then
4 (unexpected exception), then 3 (required runtime binding unavailable or
required digest/equality cannot be established), then 1 (semantic failure),
then 0 (all predicates pass). Runtime rows do not require the flag merely to
identify their matrix row; `--require-runtime` forces runtime resolution for
otherwise non-runtime inspection, while matrix-required runtime rows always
fail if their required evidence cannot be established.

The complete code list is authoritative in `x_error_code_definitions`:
`ERD-001`, `ERD-002`, `ERD-003`, `ERD-004`, `ERD-005`, `ERD-006`,
`ERD-007`, `ERD-008`, `ERD-009`, `ERD-010`, `ERD-011`, `ERD-012`,
`ERD-013`, `ERD-014`, `ERD-015`, `ERD-016`, `ERD-017`, `ERD-018`,
`ERD-019`, `ERD-020`, `ERD-021`, `ERD-022`, `ERD-023`, `ERD-024`,
`ERD-025`, `ERD-026`, `ERD-027`, `ERD-028`, and `ERD-029`.
In particular, `ERD-019` is Runner/README
status mismatch, `ERD-020` is argument/metadata mismatch, `ERD-021` is a
noncanonical `--schema`, `ERD-022` is unresolved kind/status omission,
`ERD-023` is missing terminal/log evidence, `ERD-024` is missing partial
partition evidence, `ERD-025` is missing replacement evidence, and
`ERD-026` is an unclassified dirty-source policy, `ERD-027` is a
no-replace evidence collision, `ERD-028` is evidence publication I/O,
concurrent-authentication, or digest failure, and `ERD-029` is missing
canonical terminal evidence after a pre-resource-planner failure. This
Markdown is rationale;
the JSON is the only checker lookup authority.

## 6. Duplicate disposition and ownership

Every identified overlapping rule has one disposition. `retain` means the
surface keeps its own fact; `delegate` means it calls or references the r9
checker; `convert` means its prose becomes a thin slot/binding adapter; `remove`
means the duplicated semantic rule is deleted from that surface. No surface
may implement a second slot oracle.

| Surface | Existing overlapping rule | Disposition | Sole owner after r9 | Regression property |
| --- | --- | --- | --- | --- |
| `agents/skills/experiment-lifecycle.md` | README field list, edit order, direct-run/notebook rules | convert | r9 contract for README; lifecycle workflow for operations | Workflow still fixes entrypoint/config/notebook boundaries. |
| `.agents/skills/experiment-lifecycle/SKILL.md` | Public copy of lifecycle README rules | delegate | AgentCanon source skill | Projection matches source. |
| `agents/workflows/experiment-workflow.md` | Preparation prompts and report/result order | convert | r9 slots plus workflow stages | Stages remain; heading order is not a gate. |
| `agents/workflows/long-form-writing-workflow.md` | Reader-order drafting rule | convert | r9 graph plus writing adapter | Reader order can be any graph-compatible projection. |
| `documents/experiment-registry.md` | `topic_readme` content and command/config list | retain + delegate | Registry for identity; r9 for semantics | Path/command/config checks remain single-owned. |
| `tools/ci/check_experiment_registry.py` | Topic path/command/config checks | retain + delegate | Registry structural checker | Exactly one r9 invocation; no copied slot checks. |
| `documents/coding-conventions-experiments.md` | README/run/artifact conventions | retain + delegate | Convention doc for operational conventions; r9 for semantic fields | Direct-debug and managed-run boundary remains. |
| `documents/experiment_runner.md` | README must list runner facts | convert | ExperimentRunner for runtime facts; r9 for binding | ExecutionResult/resource ownership remains. |
| `documents/experiment-runner-ff97-lifecycle.md` | Lifecycle/status completion facts | retain | Runner lifecycle | Terminal state stays runtime-owned. |
| `tools/experiments/run_managed_experiment.py` | Fixed generated report headings | convert | Runner for manifest generation; r9 for README | Manifest paths/digests remain valid; heading list is not canonical. |
| `tools/experiments/execution_resource_plan.py` | Resource/GPU certificates and noncanonical terminal/partial witnesses | convert | Resource planner for resource facts; Runner for canonical sibling evidence | Canonical sibling files cannot be written by the planner. |
| `agents/skills/experiment-review.md` | README readiness and runtime checklist | delegate + retain | r9 for README; review for direct/GPU/notebook checks | Review reports checker findings once. |
| `.agents/skills/experiment-review/SKILL.md` | Public review copy | delegate | Source review skill | Projection alignment. |
| `agents/skills/structure-planning.md` | Linear `ordered_structure` and OOP pre-order | convert | r9 semantic graph; structure skill for optional projection | Reordered complete README passes; no OOP proxy. |
| `.agents/skills/structure-planning/SKILL.md` | Public structure copy | delegate | Source structure skill | Projection alignment. |
| `agents/skills/long-form-writing.md` | Short summary/roadmap/chunking guidance | convert | r9 evidence; writing for layout | Thin content fails by evidence, not length; cohesive units stay whole. |
| `.agents/skills/long-form-writing/SKILL.md` | Public writing copy | delegate | Source writing skill | Projection alignment. |
| `agents/skills/report-writing.md` | Generic report structure and quality checklist | retain + delegate | Report-writing for narrative; r9 for experiment slots | Report quality never certifies README slots. |
| `.agents/skills/report-writing/SKILL.md` | Public report copy | delegate | Source report skill | Projection alignment. |
| `agents/skills/result-artifact-writeout.md` | Result/report placement | retain + convert | Raw artifacts and proposed result README placement | Raw artifacts stay under result; report stays under report. |
| `.agents/skills/result-artifact-writeout/SKILL.md` | Public result placement copy | delegate | Source result skill | Projection alignment. |
| `agents/skills/save-experiment-results.md` | Result retention/publish boundary | retain | Save-results skill | Branch-safe retention remains. |
| `.agents/skills/save-experiment-results/SKILL.md` | Public retention copy | delegate | Source save skill | Projection alignment. |
| `experiments/_template/README.md` | Fixed plan headings | convert | r9 contract | One-heading/thin scaffold fails; reordered complete passes. |
| parent `experiments/_template/README.md` | Parent fixed headings | deferred projection | Parent after source integration | Parent has no independent semantics. |
| `agents/templates/experiment_report.md` | Fixed report order | convert | Report-writing plus r9 mode | Reader-specific order remains free. |
| `documents/experiment-report-style.md` | IMRaD+ report list | retain + delegate | Report style for narrative | Report style does not check plan slots. |
| `tools/agent_tools/evaluate_report_quality.py` | Regex section/quality targets | retain | Generic report evaluator | No README semantic target. |
| `evidence/agent-evals/report_quality_eval.toml` | Report target manifest | retain | Report eval manifest | Targets stay report/skill surfaces. |
| `agents/canonical/ARTIFACT_PLACEMENT.md` | Run/durable placement | retain | Artifact placement | Placement remains canonical. |
| `tools/experiments/publish_result_branch.py` | Published result identity | retain | Result publisher | Result branch identity remains exact. |
| `tools/experiments/update_latest_result.py` | Latest result pointer | retain | Latest-result tool | Pointer remains exact. |
| `documents/result-log-retention-and-visualization.md` | Retention/report paths | retain | Retention document | Retention policy remains. |
| `.agents` public SKILL views generally | Duplicated source prose | delegate | Canonical source plus sync | No direct view edits. |
| parent hub/readme views | Navigation and local template copy | deferred projection | Parent integration owner | Parent follows pin/root sync. |


## 7. Run manifest evidence binding and Runner materialization

The runtime evidence paths are not implicit. Every managed
run_manifest.json contains:

A pre-finalization `run:running` manifest may omit the evidence objects. The
objects become mandatory when `finalize_run_manifest` writes a finalized
manifest; all terminal statuses then require the exact fields below.

| JSON pointer | Exact value/shape | Required by |
| --- | --- | --- |
| /evidence | object | Any run manifest carrying evidence refs. |
| /evidence/terminal_evidence/path | relative string exactly terminal_evidence.json | Every terminal runtime status. |
| /evidence/terminal_evidence/schema_version | exact terminal-evidence/v1 | Every terminal runtime status. |
| /evidence/terminal_evidence/present | boolean equal to filesystem existence | Every terminal runtime status. |
| /evidence/terminal_evidence/sha256 | lowercase SHA-256 of exact canonical bytes | Every terminal runtime status. |
| /evidence/partial_evidence/path | relative string exactly partial_evidence.json | Partial runtime status. |
| /evidence/partial_evidence/schema_version | exact partial-evidence/v1 | Partial runtime status. |
| /evidence/partial_evidence/present | boolean equal to filesystem existence | Partial runtime status. |
| /evidence/partial_evidence/sha256 | lowercase SHA-256 of exact canonical bytes, or null when absent | Every finalized runtime status. |

`tools/experiments/run_managed_experiment.py` is the one canonical producer.
It directly emits the in-memory Runner outcome to
`experiments/<topic>/result/<run_name>/terminal_evidence.json` and, only for a
partial outcome, `partial_evidence.json`; there is no filesystem source and no
copy or symlink fallback. The bytes are UTF-8 JSON with sorted keys, compact
separators, and one final LF. A SHA-256 of those exact bytes is bound in the
manifest. The resource planner may retain noncanonical diagnostic witnesses
only at
`experiments/<topic>/result/<run_name>/resource_plan/{terminal_evidence.json,partial_evidence.json}`;
it never writes the canonical sibling files.

The lifecycle write point is
`run_managed_experiment.py:finalize_run_manifest`: construct one validated
`RunnerEvidenceOutcome`, publish partial before terminal for a partial outcome,
compute digests, bind `/evidence`, write `run_manifest.json`, then write
`artifact_manifest.json`. The source-config preflight branch, including a
missing `experiments/<topic>/config.yaml`, calls this same finalizer before
resource-planner entry. It emits `terminal-evidence/v1` with
`status=failed`, `failure_code=missing_source_config`,
`failure_stage=source_config_preflight`, and no partial file.

### Payload schemas and invariants

The JSON `x_evidence_payload_schemas` object is the exact payload contract.
Both payloads are UTF-8 JSON without a BOM, with compact sorted-key canonical
bytes and one final LF. Terminal evidence has exactly these fields: `schema_version`
(`terminal-evidence/v1`), `terminal_event_id` (non-empty bounded identifier),
`status` (`complete|failed|partial|superseded`), `terminal_timestamp` (UTC
second-precision timestamp ending in `Z`), `exit_code` (integer or null),
`failure_code` (the declared enum or null), `failure_stage` (the declared enum
or null), `stop_reason` (declared enum or null), `partition` (the exact
partition object or null), `replacement_run_name` (identifier or null),
`topic` and `run_name` (identifiers), `run_manifest_relative_path`
(`run_manifest.json`), and `provenance` (the exact closed object in JSON).

Complete is exact: `exit_code=0`, `failure_code=null`,
`failure_stage=null`, `stop_reason=null`, `partition=null`, and
`replacement_run_name=null`. Superseded is exact:
`failure_code=superseded_replacement`, `failure_stage=supersession`,
`exit_code=null`, `stop_reason=null`, `partition=null`, and a non-null
`replacement_run_name`. Missing-source-config is exact:
`failure_code=missing_source_config`, `failure_stage=source_config_preflight`.
The ordinary nonzero process-exit path is exact:
`failure_code=command_exit_nonzero`, `failure_stage=managed_command`.
Partial terminal evidence is exact: `failure_code=partial_stop`,
`failure_stage=partial_finalization`, a non-null `stop_reason` and partition,
and no replacement name.
The closed failed-outcome algebra has exactly five reachable pairs:
`missing_source_config/source_config_preflight`,
`command_exit_nonzero/managed_command`, `timeout/managed_command`,
`resource_planner_failure/resource_planner`, and
`runner_failure/runner_finalization`. Each pair is emitted only by its named
factory and boundary in the JSON contract. `partial_stop/partial_finalization`
and `superseded_replacement/supersession` are non-failed status outcomes, not
failed pairs. `evidence_materialization_collision/evidence_publication` and
`evidence_materialization_io/evidence_publication` are producer-result
classifications (`RunnerEvidencePublication` with `collision` or `io`), not
constructible `RunnerEvidenceOutcome` pairs; no terminal payload or finalized
manifest is fabricated for either. Arbitrary code/stage tuples are
unconstructible.

Partial evidence has exactly these fields: `schema_version`
(`partial-evidence/v1`), `terminal_event_id`, `status=partial`,
`terminal_timestamp`, `exit_code` (integer or null),
`failure_code=partial_stop`, `failure_stage=partial_finalization`,
`partial_is_completion=false`, `stop_reason`, `partition`, `topic`,
`run_name`, `run_manifest_relative_path=run_manifest.json`, and the same
closed `provenance` object. `partition` has exactly five arrays:
`universe`, `completed`, `failed`, `in_flight`, and `unstarted`. Arrays contain
sorted unique case IDs; the four state arrays are pairwise disjoint, each is a
subset of `universe`, and their union equals `universe`. Empty states are `[]`,
never null or omitted. No case ID may occur twice.

Provenance is normalized to repository-relative POSIX paths, normalized
second-precision UTC timestamps, stable identifiers, sorted arrays, and
single-line UTF-8 strings. Missing preflight paths/digests are explicit nulls;
fields are not silently omitted.

### Runner outcome and no-replace publication

`RunnerEvidenceOutcome` is a frozen typed record. The only constructors are
the JSON-defined complete, missing-source-config, process-exit, timeout,
resource-planner-failure, RunnerFailure, partial, and superseded factories.
The exact signatures are `build_runner_evidence_outcome(context, *,
exit_code)`, `build_missing_source_config_outcome(context, *, exit_code,
message)`, `build_timeout_outcome(context, *, exit_code, timeout_seconds,
message)`, `build_resource_planner_failure_outcome(context, *, planner_error,
resource_plan_path)`, `build_runner_failure_outcome(context, *, error)`,
`RunnerEvidenceOutcome.partial(...)`, and
`RunnerEvidenceOutcome.superseded(...)`. `emit_runner_evidence(context,
outcome)` and `finalize_run_manifest(context, manifest, start_monotonic,
outcome, patterns)` return the typed `RunnerEvidencePublication` result.
Existing `run_cli` maps zero to complete and nonzero to failed
`command_exit_nonzero`; the preflight branch uses the named missing-config
factory, while timeout, planner, and RunnerFailure use their named typed
boundaries. Workers do not invent status/code/stage tuples, partial/superseded
outcomes, publication errors, or destinations.

Publication is race-safe and no-replace. Open a unique temp name in the
destination directory with `O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC`, write all
canonical bytes, `fsync` the temp file, then publish with `os.link` using the
same directory descriptor. `os.replace` and rename-over-destination are
forbidden. After linking, fsync the directory and unlink the creator-owned
temp file, followed by another directory fsync. There is no check-then-
replace sequence.

If `os.link` returns `EEXIST`, authenticate the existing destination with
`O_NOFOLLOW`, require a regular file, fstat before and after reading, and
accept only unchanged exact bytes and matching SHA-256. Equal concurrent
writers yield one publication and idempotent success for losers. Different
writers yield one publication and `ERD-027` for losers; symlink/non-regular
or changing authentication and cleanup failures yield `ERD-027` or `ERD-028`.
No caller replaces or deletes a destination it did not create.

The resource planner receives both required, independently resolved
roots: `result_dir=context.paths.result_dir` and the local
`runtime_root` resolved by `execute_managed_run`. It derives
`result_witness_root=result_dir/resource_plan` internally through
`derive_resource_plan_roots(result_dir, runtime_root)`. Its exact call is
`run_resource_plan(plan, result_dir=context.paths.result_dir,
runtime_root=runtime_root)` and its CLI is
`execution_resource_plan.py --plan PLAN_JSON --result-dir
experiments/<topic>/result/<run_name> --runtime-root RUNTIME_ROOT`.
Planner witness writes are confined to `result_dir/resource_plan`; existing
resource/certificate persistence remains allowed below `runtime_root` and is
owned by the resource planner/runtime persistence boundary. The planner may
not open or publish `result_dir/terminal_evidence.json` or
`result_dir/partial_evidence.json`. The focused planner oracle partitions
observed writes by these two roots, preserves runtime-root side effects, and
asserts only that the canonical siblings remain untouched.

## 8. Result README boundary

Current AgentCanon evidence has no canonical result README; result-writeout
routes human reports to `experiments/report/<run_name>.md`. The r9 contract
places the artifact-local result README at
`experiments/<topic>/result/<run_name>/README.md`. Its content/placement owner
is agents/skills/result-artifact-writeout.md; its latest-result pointer and
status producer/edit owner is tools/experiments/update_latest_result.py.
That tool must add /result_readme/{path,kind,status,run_name} to LATEST.json.
The path is the absolute result_dir/README.md string, kind is result, status is
one of running|complete|failed|partial|superseded read from the exactly-one
result README metadata block, and run_name is the metadata run name.
tests/tools/test_update_latest_result.py owns the reachable pointer regression.
The semantic slot property remains solely in check_experiment_readme.py; the
report remains owned by report-writing.

## 9. Integration and non-goals

AgentCanon canonical source is edited first and reviewed. The parent then owns
the submodule pin and runs `bash tools/sync_agent_canon.sh link-root` followed
by `bash tools/sync_agent_canon.sh check`; parent templates/hubs are edited only
after that integration. Public `.agents` views are generated projections.

This audit packet does not edit source, create implementation tests, run an
experiment/GPU/notebook, or weaken the semantic oracle. The single future
semantic validation route is `check_experiment_readme.py`; Markdown,
dependency, registry-structure, and runtime-certificate tools retain their
mechanical/runtime owners and do not duplicate its predicates.


## 10. r9 closure decisions

The matrix carries a stable predicate ID for every allowed kind/status pair and
directly encodes terminal, log, partial-partition, replacement, dirty-source,
Runner-status, observed-claim, forward-reference, and runtime-flag predicates.
Failed rows require terminal and log evidence; partial rows require terminal,
logs, and mutually exclusive completed/failed/in-flight/unstarted partitions;
superseded rows require terminal evidence and a replacement link.

Runner `completed` maps exactly to README `complete`; `running` and
`failed` map identically, and terminal evidence uses the same normalized
value. `partial` and `superseded` require explicit lifecycle outcomes.
`run_managed_experiment.py` directly produces the canonical sibling evidence
files, including the missing-source-config preflight path, before it writes
the run manifest. `execution_resource_plan.py` is only a noncanonical
diagnostic witness producer under the explicit `resource_plan/` directory.
Lifecycle validation is owned by
`experiment-lifecycle.md`, with one registry delegation and
`experiment-review.md` consuming the result.

The result README remains
`experiments/<topic>/result/<run_name>/README.md`, owned by
`result-artifact-writeout.md`, with the pointer boundary in
`update_latest_result.py` and the semantic boundary in
`check_experiment_readme.py`. No universal heading order is prescribed.
No word, character, section, heading, line-count, or OOP proxy is a contract
predicate. Cohesive semantic units remain intact.

## 11. r9 Runner boundary closure

### Failure factories

The factories are closed and their construction sites are not interchangeable:

| Pair | Factory and construction site | Available provenance | Manifest/status result | Single validation owner |
| --- | --- | --- | --- | --- |
| `missing_source_config/source_config_preflight` | `build_missing_source_config_outcome` at `run_cli` source-config preflight, before planner entry | preflight stage, missing path/status, command/config/source/environment fields, timestamps, sanitized message | `terminal.status=failed`; `run_manifest.status=failed`; planner not entered | `tests/tools/test_run_managed_experiment.py::test_missing_source_config_factory_and_manifest_binding` |
| `command_exit_nonzero/managed_command` | `build_runner_evidence_outcome` immediately after the managed process returns nonzero | exact exit code, command, captured logs, config/source/environment paths and digests, timestamps | `terminal.status=failed`; `run_manifest.status=failed` | `tests/tools/test_run_managed_experiment.py::test_nonzero_exit_factory_and_manifest_binding` |
| `timeout/managed_command` | `build_timeout_outcome` at the managed-command timeout adapter | timeout seconds/deadline, signal/known exit code, command, logs, bindings, timestamps | `terminal.status=failed`; `run_manifest.status=failed` after evidence publication | `tests/tools/test_run_managed_experiment.py::test_timeout_factory_and_manifest_binding` |
| `resource_planner_failure/resource_planner` | `build_resource_planner_failure_outcome` at the Runner resource-plan invocation adapter | typed planner error, planner path, result witness root, runtime root, planner-entered flag, bindings, timestamps | `terminal.status=failed`; `run_manifest.status=failed`; runtime-root side effects remain separately attributed | `tests/tools/test_run_managed_experiment.py::test_resource_planner_failure_factory_and_manifest_binding` |
| `runner_failure/runner_finalization` | `build_runner_failure_outcome` at the typed `RunnerFailure` boundary in `run_cli`/finalization | sanitized error class/code/message, lifecycle stage, known exit code, bindings, timestamps | `terminal.status=failed`; `run_manifest.status=failed` only if evidence publication succeeds | `tests/tools/test_run_managed_experiment.py::test_runner_failure_factory_and_manifest_binding` |

Publication collision and I/O are not additional failed pairs. The typed
`RunnerEvidencePublication` result is the sole authority for them: expected
`FileExistsError`, `OSError`, `ValueError`, and `UnicodeError` are caught and
returned as `collision` or `io`; no exception escapes the publication boundary,
and `run_cli` writes no finalized manifest. An unexpected non-publication
exception reaches the typed `RunnerFailure` boundary.

### RunnerEvidencePublication

`RunnerEvidencePublication` is a frozen record with exactly these fields:
`outcome` (`published|idempotent_existing|collision|io`),
`destination_path` (repo-root-relative POSIX canonical sibling),
`content_sha256` (attempted canonical bytes or null before serialization),
`existing_sha256` (authenticated existing regular file digest or null),
`cleanup_status` (`not_needed|cleaned|cleanup_failed`), `errno` (integer or
null), `reason_code` (the closed JSON enum), `reason` (single-line UTF-8 or
null), `exception_type` (null, `FileExistsError`, `OSError`, `ValueError`, or
`UnicodeError`), `temp_path` (relative path or null), `serializer`
(`canonical_json_v1`), and `publication_method`
(`temp_create_fsync_link_no_replace`). `emit_runner_evidence` and
`finalize_run_manifest` return this record for all expected outcomes.
`published` and `idempotent_existing` permit exact evidence binding and then
manifest publication; `collision` and `io` abort finalization and return
`EVIDENCE_PUBLICATION_FAILURE_EXIT_CODE=2` without replacing any destination.

### Partial finalization aggregate

`RunnerEvidencePublicationAggregate` is the exact return from
`finalize_partial_evidence` and from `finalize_run_manifest` when the outcome
is partial. It contains `partial_result` and `terminal_result`, each an
independent `RunnerEvidencePublication`, plus `partial_admitted`,
`terminal_admitted`, `admitted`, the fixed attempt order
`[partial_evidence.json, terminal_evidence.json]`, aggregate `status`, retry,
cleanup, manifest-update, retained-marker, and `process_return_code` fields.

The only aggregate statuses are `success_published`,
`success_idempotent_existing`, `success_mixed`,
`partial_admitted_terminal_failure`, and `partial_publication_failure`.
Partial evidence is always attempted first. Terminal evidence is attempted
only after partial publication is `published` or `idempotent_existing`.

If partial is admitted and terminal publication returns `collision` or `io`,
the aggregate is `partial_admitted_terminal_failure`, the admitted partial
file is retained, and `retained_orphan_marker` records
`partial_evidence.json`, its digest, missing terminal evidence, unpublished
manifest state, and `deletion=forbidden`. If partial publication itself
returns `collision` or `io`, terminal publication is not attempted and the
aggregate is `partial_publication_failure`.

Only each publisher may clean its own unadmitted temporary file. No caller
may delete, replace, unlink, or roll back admitted evidence. A retry uses the
same canonical bytes; equal existing bytes become `idempotent_existing`, and
different, symlink, or non-regular destinations remain collisions.

`run_manifest.json` is written only after both artifacts are admitted and
their exact digests are bound. Either aggregate failure leaves the existing
pre-finalization manifest unchanged. Successful finalization returns the
underlying outcome exit code when it is an integer, otherwise `0`; either
publication-failure status returns exactly `2` through `run_cli` and `main`.

### Runner runtime-root and dual-root planner boundary

`execute_managed_run(context, run_config)` remains the Runner API. It resolves
`AGENT_CANON_SHARED_RUNTIME_SOURCE` locally (default and only accepted value
`/var/lib/agent-canon/runtime`), validates an absolute existing directory, and
uses `dataclasses.replace(request, runtime_root=runtime_root)`; `RunContext` is
not expanded. `build_run_environment(context)` remains the source of the run
environment; runtime-root resolution is a separate execute-boundary check.

The exact APIs are
`derive_resource_plan_roots(result_dir: Path, runtime_root: Path) ->
ResourcePlanRoots` and
`run_resource_plan(plan: ResourcePlan, *, result_dir: Path, runtime_root:
Path) -> ResourcePlanResult`. The exact Runner call, after `frozen_plan` is
complete and before `StandardRunner` construction, is:

```text
run_resource_plan(
    frozen_plan,
    result_dir=context.paths.result_dir,
    runtime_root=runtime_root,
)
```

`result_dir/resource_plan/` is the planner's result-witness root and
`runtime_root/` is the existing resource/certificate persistence root. The
canonical evidence siblings remain Runner-owned. Focused tests validate local
resolution, environment mismatch, absolute/separate roots, exact call shape,
runtime-root side effects, and canonical sibling absence.


## 12. r9 authority and non-goals

The r9 JSON is the only lookup authority. All r2/r3/r4/r5/r6/r7/r8 contract
and review artifacts are historical evidence and cannot route worker decisions.
The fresh-worker return authority is fresh-worker-return-schema.json with
contract_revision=r9 and validation route experiment-readme-contract-r9.

No universal heading order is prescribed. No word, character, section, heading,
line, token, density, or OOP proxy is a completeness, split, or acceptance
predicate. Reordered complete READMEs pass; semantically thin READMEs fail;
cohesive units remain intact.
