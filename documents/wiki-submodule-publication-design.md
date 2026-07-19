<!--
@dependency-start
contract design
responsibility Defines the target-state GitHub Wiki publication, parent projection, and preserved-sibling cleanup boundary.
upstream design ../AGENTS.md repository scope, ownership, and design-integrity contract.
upstream design ../vendor/agent-canon/CONTAINER_OPERATIONS.md shared submodule and devcontainer ownership.
upstream design ../vendor/agent-canon/agents/skills/structure-refactor.md structure review contract.
upstream design ../vendor/agent-canon/documents/dependency-manifest-design.md dependency-header contract.
upstream design ./template-github-remote.md template remote and submodule precedent.
upstream design ./template-bootstrap.md clone and bootstrap precedent.
downstream implementation ../.gitmodules parent submodule declaration.
downstream design ./README.md documents index and ownership projection.
downstream design ../README.md parent documentation entrypoint projection.
@dependency-end
-->

# Wiki Submodule Publication Design

This is the canonical, target-state-first design for one parent-visible GitHub
Wiki submodule. The current remote state is REMOTE_UNINITIALIZED; that blocks
all future materialization, source editing, publication, pinning, and cleanup,
but does not block this design repair. This task ends after independent detailed
design and document-flow review. It does not poll a remote or implement any
future stage.

## Target state first

The completed state, which must be true before any future edit instruction is
actionable, is:

1. The parent has exactly one wiki/ gitlink at mode 160000, pointing at the Wiki
   remote default branch and the approved snapshot.
2. The GitHub Wiki remote is the sole content and reader authority. Its workflow
   owns page creation, page set, Home.md, navigation, formatting, link/style
   checks, document-flow review, content review, and immutable approval.
3. AgentCanon owns only reusable capability, owner-based routing, transport and
   record contracts, generic structure support, and focused generic tests. It
   contains no parent URL, parent SHA, Wiki page list, or Wiki semantic oracle.
4. The parent owns only concrete projection and gitlink integrity, parent clone
   and devcontainer behavior, and parent-owned documents. It copies snapshot
   identity and digests; it never enumerates or reruns Wiki semantic checks.
5. Wiki remains publication-only and contains no raw report, evidence, run-bundle,
   evaluation, proof, issue, or policy canon. Those remain in their owner
   repositories and are linked immutably.
6. The sibling /mnt/l/workspace/project_template.wiki is preserved evidence
   until all remote, merged-parent, fresh-clone, and reachability conditions pass.
   One separately authorized exact-path cleanup transition then makes it absent.
   There is no compatibility phase and no local-only or unreachable gitlink.

The target-state graph is:

~~~mermaid
flowchart LR
  P[Parent main] --> GM[.gitmodules]
  GM --> W[wiki gitlink mode 160000]
  W --> R[GitHub Wiki remote]
  R --> WR[Wiki reader and rendered pages]
  A[AgentCanon generic capability] --> T[transport record router structure]
  P --> PC[parent config clone container docs]
  S[preserved sibling evidence] -. exact cleanup transition .-> X[sibling absent]
  O[owner reports and evidence] -. immutable links .-> WR
~~~

This graph answers which repository owns each surface. It does not authorize
publication, deletion, a Git mutation, or a parent PR.

## Normative future stage map

The following order is normative and is identical in the implementation packet.
Every stage after stage 0 is future work; a failed precondition stops the
sequence and emits its typed record.

| Stage | Required transition | Sole owner and gate | Forbidden shortcut |
| --- | --- | --- | --- |
| 0 | Record target state, ownership, exact paths, preserved-sibling status, and complete this design plus independent reviews. | Design workflow; terminal APPROVE | Remote polling, source edit, Git mutation |
| 1 | Materialize the remote, then run symbolic remote-materialization preflight. | Wiki/remote operator; transport identity and DEFAULT_BRANCH gate | Any source edit while REMOTE_UNINITIALIZED |
| 2 | Implement and independently review the generic AgentCanon publisher-consumer capability after stage 1. | AgentCanon; schema/identity/digest/transport gate | Parent-specific values or a Wiki semantic oracle in AgentCanon |
| 3 | Write the exact candidate in the Wiki-owned checkout and run candidate-owned format/link checks. | Wiki writer workflow; candidate content/navigation/format/style gate | Parent editing wiki/Home.md or AgentCanon judging page semantics |
| 4 | Independently review and check that exact candidate without publishing it. | Independent Wiki reviewer; candidate commit/tree and semantic review gate | Writer self-approval or review of a moving candidate |
| 5 | After stage 4 passes, freeze one immutable Wiki approval record for that exact candidate. | Wiki approval recorder; approval schema/digest gate | Publication producing its own prerequisite approval |
| 6 | Publisher first consumes and validates the stage-5 approval record, then publishes only its exact candidate identity. | AgentCanon publisher-consumer; approval identity/digest and CAS gate | Publishing before approval consumption or changing the candidate |
| 7 | Run Wiki-owned semantic readback against the published identity and freeze its record. | Wiki semantic checker; rendered reader readback gate | AgentCanon calculating page/link coverage or semantic status |
| 8 | Run sync-parent from approved readback and open the parent pin PR. | Parent; projection transaction and parent review | Local gitlink before approved readback |
| 9 | Review and merge the parent pin PR. | Parent repository workflow | Treating an unmerged projection as merged evidence |
| 10 | Read back the merged parent commit and verify concrete gitlink/config identity. | Parent; merged-parent readback gate | Cleanup assessment against an unmerged parent |
| 11 | Run a fresh recursive clone and exact fixture verification. | Parent; fresh-clone gate | Reusing the mutable working clone as proof |
| 12 | Run read-only cleanup-ready and emit the versioned cleanup proof. | Operator using Wiki/parent evidence | Deleting anything or granting deletion authority |
| 13 | Obtain separate explicit destructive authority, immediately recheck fingerprint, and delete exactly the allowlisted sibling. | Named operator; exact-path cleanup gate | Compatibility retention, broad cleanup, implicit authority |

The current task performs only stage 0. “No AgentCanon source edit” therefore
means no AgentCanon source edit in this task; stage 2 is future work and is
blocked until stage 1 has materialized the remote.

## Abstract design frame and gate ownership

~~~text
Layer 0 — Wiki authority:
  remote default branch, pages, Home/navigation, rendering, semantic checks,
  candidate checks, independent content/document-flow review, immutable
  approval-record production, and post-publication semantic readback.

Layer 1 — AgentCanon generic capability:
  typed lifecycle transport, immutable-record schema/identity/digest checks,
  capability/owner routing, approval-record consumption, exact-candidate CAS
  publication, generic structure support, and focused tests.

Layer 2 — Parent projection:
  concrete config, .gitmodules, mode-160000 gitlink, merged-parent readback,
  recursive clone, devcontainer safe directories, and parent-owned docs.

Layer 3 — Transition evidence:
  ignored run-local records, cleanup proof, and one explicitly authorized
  exact-path deletion. It is never Wiki raw-evidence canon.
~~~

| Gate/property | Sole owner | Included checks | Explicitly excluded |
| --- | --- | --- | --- |
| Candidate page set, page content, Home.md, navigation, formatting, links, style, and reader flow | Wiki writer workflow | Candidate-owned checks bound to exact commit/tree | Approval, publication, Parent checks, AgentCanon semantic judgment |
| Independent candidate review/check | Independent Wiki reviewer | Exact candidate identity and semantic decision | Publication or writer self-approval |
| Immutable approval record production | Wiki approval recorder | Stage-4 result, closed schema, exact candidate identity, canonical digest | Publication, transport mutation, AgentCanon semantic judgment |
| Approval-record consumption and exact-candidate publication | AgentCanon publisher-consumer | Record schema/version/canonical bytes/identity/digest, ordering, CAS, remote transport | Producing its prerequisite approval record or judging pages/links |
| Published-page semantic readback production | Wiki semantic checker | Exact published identity, rendered page/link semantics, closed readback record | AgentCanon or Parent calculating semantic_status |
| Readback record consumption | AgentCanon and Parent | Closed schema, identity, canonical digest, approval linkage, ordering, transport/reader availability | Page-set membership, navigation, content, formatting, style, document-flow judgment |
| Generic capability, owner router, manifest structure support, focused tests | AgentCanon | Generic URL-agnostic tests | Parent values and Wiki semantic fixtures |
| Parent config, .gitmodules, gitlink, merged-parent readback | Parent | Concrete URL/branch/SHA/tree, config and gitlink integrity | Wiki semantic checks |
| Parent clone, fixture, container and safe-directory behavior | Parent | Recursive clone, exact pin, parent-owned docs and container behavior | Wiki rendering/content review |
| Sibling cleanup | Operator | Versioned proof, exact allowlist, immediate recheck, separate authority | cleanup-ready deletion |

The parent and AgentCanon may copy or pin only the approval record snapshot
identity and immutable digest. Neither may enumerate its page arrays or run a
semantic Wiki check. A record array is opaque to them except for canonical-byte
and digest verification.

## Fixed identities and exact scope

| Symbol | Exact meaning |
| --- | --- |
| WIKI_REMOTE_URL | https://github.com/iwashita-nozomu/project_template.wiki.git |
| WIKI_READER_URL | https://github.com/iwashita-nozomu/project_template/wiki |
| PARENT_API_OWNER | iwashita-nozomu |
| PARENT_API_REPOSITORY | project_template |
| WIKI_SUBMODULE_PATH | wiki |
| APPROVED_SHA | 05e3bb317410bcaf2db60a9df8f72154bd8f7629 |
| APPROVED_TREE | 891d2abf3e88d7ccdb5e488622969464abedfe21 |
| DEFAULT_BRANCH | Single branch returned by symbolic HEAD; never guessed |
| SOURCE_DIR | Run-local Wiki source checkout input only; never committed |
| SIBLING_PATH | Run-local input, allowed only as the exact path below |
| WIKI_APPROVAL_RECORD | Wiki-owned semantic approval record, opaque to AgentCanon and parent |

The only permitted sibling reads in a future source packet or cleanup proof are:

~~~text
/mnt/l/workspace/project_template.wiki/Home.md
/mnt/l/workspace/project_template.wiki/Reports-and-Evidence.md
/mnt/l/workspace/project_template.wiki/wiki-coverage.json
~~~

wiki-coverage.json is noncanonical Wiki-owned evidence. It is not source canon,
parent config, raw-report canon, or a reason to read any other sibling path.
Every other path under /mnt/l/workspace/project_template.wiki, including .git,
other Markdown pages, generated files, and hidden files, is forbidden for read,
write, glob, search, status, or deletion. The sibling is never edited by the
parent, AgentCanon, or this task.

This source-packet prohibition is distinct from the cleanup safety algorithm:
cleanup may perform the mandatory Git metadata/status probes and content
fingerprinting required by the Cleanup safety proof, but those probes are
safety evidence only, never source/content consumption or imported evidence.
They may not copy or publish sibling content, and no other lifecycle stage may
open a sibling path.

## Immutable approval and readback records

### One JSON envelope

Every future subcommand emits exactly one UTF-8 JSON object and no human prose.
The object has this exact envelope:

~~~json
{
  "schema": "agentcanon.wiki_publication.envelope",
  "schema_version": 1,
  "command": "<subcommand>",
  "request_id": "<caller supplied UUID>",
  "status": "ok",
  "exit_code": 0,
  "failure": null,
  "result": {},
  "record_sha256": "<sha256 of canonical result record or null>",
  "written_paths": [],
  "observed_identities": {}
}
~~~

status is one of ok, idempotent, or error. failure is null for success and
otherwise exactly {"code":"<typed code>","stage":"<stage>"}. result,
written_paths, and observed_identities have command-specific keys listed below;
unknown keys are rejected. Canonical JSON is UTF-8, sorted keys, no insignificant
whitespace, and LF-only. record_sha256 hashes canonical record bytes before the
envelope is emitted. A record is immutable: duplicate request_id must have the
same command, input digest, record bytes, and result, or it fails with
REQUEST_ID_REUSE_CONFLICT.

### Wiki-owned semantic approval record

After the writer checks the frozen candidate, an independent Wiki reviewer
checks that same commit/tree. Only a passing independent result lets the Wiki
approval recorder produce WIKI_APPROVAL_RECORD. The recorder does not publish;
the immutable record is the sole semantic prerequisite and has this schema:

~~~json
{
  "schema": "wiki.semantic-approval",
  "schema_version": 1,
  "record_id": "<UUID>",
  "approval_status": "approved",
  "remote_url": "<WIKI_REMOTE_URL>",
  "default_branch": "<discovered branch>",
  "commit_sha": "<40 hex>",
  "tree_sha": "<40 hex>",
  "approved_page_paths": ["<sorted Wiki paths>"],
  "required_home_links": ["<sorted Wiki targets>"],
  "page_set_digest": "<sha256>",
  "home_links_digest": "<sha256>",
  "wiki_check_run_id": "<Wiki workflow identity>",
  "reader_url": "<WIKI_READER_URL>"
}
~~~

The Wiki workflow calculates arrays, semantic digests, page presence, link
resolution, formatting/style result, and approval. AgentCanon accepts only
approval_status=approved, verifies schema/types, canonical bytes, snapshot
identity, and the supplied immutable record digest. It does not compare array
contents to an expected list and does not fetch or parse Wiki pages.

After publication, the Wiki-owned semantic checker produces the closed
version-1 object below. No key may be omitted or added. Strings are UTF-8;
UUIDs are lowercase RFC 4122 text; SHA-1 values are 40 lowercase hexadecimal
characters; SHA-256 values are 64 lowercase hexadecimal characters.

~~~json
{
  "schema": "wiki.semantic-readback",
  "schema_version": 1,
  "record_id": "00000000-0000-4000-8000-000000000000",
  "approval_record_id": "00000000-0000-4000-8000-000000000000",
  "approval_record_digest": "<64-lowercase-hex>",
  "remote_url": "<exact-WIKI_REMOTE_URL>",
  "reader_url": "<exact-WIKI_READER_URL>",
  "default_branch": "<nonempty-Git-branch-name>",
  "commit_sha": "<40-lowercase-hex>",
  "tree_sha": "<40-lowercase-hex>",
  "semantic_status": "approved",
  "wiki_check_run_id": "<nonempty-Wiki-check-run-id>"
}
~~~

The exact key set is schema, schema_version, record_id, approval_record_id,
approval_record_digest, remote_url, reader_url, default_branch, commit_sha,
tree_sha, semantic_status, and wiki_check_run_id. schema is the literal
wiki.semantic-readback; schema_version is integer 1; semantic_status is exactly
approved or rejected. remote_url and reader_url are absolute HTTPS URLs;
default_branch is a valid nonempty branch name; wiki_check_run_id is a nonempty
string. Booleans, nulls, numbers in string fields, missing keys, and unknown or
extra keys are rejected.

Canonical bytes are UTF-8 JSON with keys sorted lexicographically, separators
comma and colon without surrounding whitespace, no BOM, and no terminal
newline. readback_record_digest is lowercase SHA-256 of those exact bytes and
is carried outside the record in the command envelope. approval_record_id and
approval_record_digest equal the consumed immutable approval record identity
and canonical-byte digest. remote_url, reader_url, default_branch, commit_sha,
tree_sha, and wiki_check_run_id equal the approval record and published
candidate fields exactly; no normalization after comparison is allowed.

| Wiki semantic evaluation | Identity/schema/digest/order/availability | Result |
| --- | --- | --- |
| approved | all valid and equal; transport and reader available | accept |
| approved | any validation or equality fails | reject with typed failure |
| rejected | otherwise valid | reject as WIKI_READBACK_NOT_APPROVED |
| missing/unavailable | record or transport/reader unavailable | reject with typed failure |

Schema, type, format, missing-key, and unknown-key failures map to
READBACK_RECORD_SCHEMA_INVALID, exit 16. Canonical-byte digest mismatch maps to
READBACK_RECORD_DIGEST_MISMATCH, exit 17. Approval linkage or candidate-field
inequality maps to APPROVED_IDENTITY_MISMATCH, exit 15. A valid rejected record
maps to WIKI_READBACK_NOT_APPROVED, exit 20. Authentication or availability
failure maps to AUTH_FAILED, exit 11; remote identity mismatch maps to
REMOTE_IDENTITY_MISMATCH, exit 12; changed remote head maps to
REMOTE_HEAD_CHANGED, exit 19.

On success the publisher-consumer emits status=ok, exit_code=0, failure=null,
and exactly this result object: remote_ref (refs/heads/<default_branch>),
remote_sha (commit_sha), remote_tree (tree_sha), approval_record_digest,
readback_record_digest, transport_available=true, and reader_available=true.
The Wiki alone owns semantic_status. AgentCanon and Parent validate only the
record identity, closed schema, canonical digest, ordering, exact equalities,
and transport/reader availability.

Run-local records use these exact paths:

~~~text
/tmp/wiki-publication/<request-id>/preflight.json
/tmp/wiki-publication/<request-id>/publish.json
/tmp/wiki-publication/<request-id>/readback.json
/tmp/wiki-publication/<request-id>/sync-parent.json
/tmp/wiki-publication/<request-id>/check.json
/tmp/wiki-publication/<request-id>/cleanup-ready.json
/tmp/wiki-publication/<request-id>/cleanup.json
/tmp/wiki-publication/<request-id>/transaction.json
/tmp/wiki-publication/<request-id>/lease
~~~

Records are ignored, run-local, and noncanonical. Each is written through a
same-directory temporary file, fsync, mode-preserving os.replace, and directory
fsync; a pre-existing record is never overwritten. The envelope is emitted only
after record digest and write are verified.

## Normative CLI contract

The future entrypoint is:

~~~bash
python3 vendor/agent-canon/tools/agent_tools/wiki_publication.py <subcommand> ...
~~~

Every subcommand requires --json and --request-id UUID. Shell expansion, prompt
text, and environment values cannot supply structured routing or identity.
remote-url must equal the configured transport identity; reader-url must equal
the configured reader identity; identities are not inferred from one another.
publish never creates or approves its prerequisite: it first consumes the
immutable Wiki approval record, validates its exact candidate linkage, and only
then mutates the remote. readback runs only after that publication and consumes
both the approval record and the Wiki-owned semantic-readback record.

| Subcommand | Required arguments | Optional arguments | Forbidden arguments/effects |
| --- | --- | --- | --- |
| preflight | remote-url, source-dir, reader-url, evidence-record, json, request-id | parent-api-owner, parent-api-repository | default-branch, approved identity, parent config, source/remote writes |
| publish | remote-url, source-dir, preflight-record, wiki-approval-record, default-branch, approved-sha, approved-tree, evidence-record, json, request-id | force-with-lease only with bootstrap authority | parent config, .gitmodules, gitlink, semantic calculation, sibling writes |
| readback | remote-url, reader-url, default-branch, wiki-approval-record, wiki-readback-record, evidence-record, json, request-id | none | page/link enumeration or semantic judgment by AgentCanon, parent/sibling writes |
| sync-parent | parent-root, config-path, submodule-path, readback-record, remote-url, default-branch, approved-sha, approved-tree, json, request-id | gitmodules-path only as parent-root/.gitmodules | source-dir, sibling-path, page arrays, Wiki checks, remote publication |
| check | parent-root, config-path, submodule-path, json, request-id | none | remote access, source-dir, sibling-path, Wiki checks, writes |
| cleanup-ready | sibling-path, readback-record, merged-parent-record, fresh-clone-record, proof-record, json, request-id | allowlisted-path, which must equal fixed sibling path | delete, force, destructive authority, broad sibling search |
| cleanup | sibling-path, cleanup-proof, confirm-realpath, json, request-id | none | any path other than fixed sibling, compatibility retention, implicit authority |

sync-parent is the only command that may write parent projection files. cleanup
is the only command that may delete anything, and only after the separate
authority transition below. All other commands are read-only except immutable
run-local records. Wiki source editing is outside this CLI and allowed only
after stage 1.

The result object has these exact command-specific required keys; no command may
add a semantic page list or an unlisted key:

| Command | Exact result keys |
| --- | --- |
| preflight | remote_state, transport_identity, reader_identity, default_branch, remote_head_sha, source_fingerprint |
| publish | published_sha, published_tree, default_branch, preflight_record_digest, approval_record_digest, lease_identity |
| readback | remote_ref, remote_sha, remote_tree, approval_record_digest, readback_record_digest, transport_available, reader_available |
| sync-parent | transaction_id, config_sha256, gitmodules_sha256, gitlink_path, gitlink_sha, gitlink_tree, preimage_sha256, postimage_sha256 |
| check | config_sha256, gitmodules_sha256, gitlink_path, gitlink_sha, gitlink_tree, projection_status |
| cleanup-ready | proof_id, allowlisted_path, realpath, fingerprint_before, merged_parent_commit, merged_parent_gitlink, fresh_clone_parent_commit, fresh_clone_gitlink, commit_closure_digest |
| cleanup | proof_id, deleted_path, deleted, fingerprint_before, fingerprint_recheck |
| route | normalized_input, catalog_digest, candidate_names, selected_name |

### Status, exit codes, and deterministic failure precedence

Exit 0 means ok or idempotent. The exact typed mapping is:

| Exit | Failure code |
| ---: | --- |
| 2 | INVALID_ARGUMENTS, INPUT_SCHEMA_INVALID, REQUEST_ID_REUSE_CONFLICT |
| 3 | CONCURRENCY_BUSY, LEASE_LOST |
| 4 | PATH_SCOPE_VIOLATION, SYMLINK_OR_MOUNT_REJECTED, SPECIAL_FILE_REJECTED |
| 10 | REMOTE_UNINITIALIZED |
| 11 | AUTH_FAILED |
| 12 | REMOTE_IDENTITY_MISMATCH |
| 13 | DEFAULT_BRANCH_UNRESOLVED |
| 14 | BOOTSTRAP_DIVERGED |
| 15 | APPROVED_IDENTITY_MISMATCH |
| 16 | APPROVAL_RECORD_SCHEMA_INVALID, READBACK_RECORD_SCHEMA_INVALID |
| 17 | APPROVAL_RECORD_DIGEST_MISMATCH, READBACK_RECORD_DIGEST_MISMATCH |
| 18 | SOURCE_DIRTY |
| 19 | REMOTE_HEAD_CHANGED |
| 20 | WIKI_APPROVAL_NOT_APPROVED, WIKI_READBACK_NOT_APPROVED |
| 30 | GITLINK_PRECONDITION_FAILED, PARENT_CONFIG_MISMATCH |
| 31 | GITMODULES_CONFLICT, PIN_DRIFT |
| 32 | PARENT_READBACK_FAILED, FRESH_CLONE_FAILED |
| 40 | DIRTY_OVERLAP, CLEANUP_NOT_READY |
| 41 | CLEANUP_OWNERSHIP_UNPROVED, CLEANUP_FINGERPRINT_CHANGED |
| 42 | DESTRUCTIVE_AUTHORITY_REQUIRED |
| 50 | RECORD_WRITE_FAILED, ATOMIC_TRANSACTION_FAILED |

Precedence is deterministic and stops at the first observable failure:
argument count/forbidden argument; JSON and record schema; request-id conflict;
lease acquisition/loss; exact-path safety; explicit authority; transport
reachability/authentication; remote identity; symbolic branch; bootstrap lease;
approved identity; source cleanliness; remote head lease; Wiki-owned approval or
readback status; parent preconditions; .gitmodules/pin state; cleanup evidence
and fingerprint; atomic write. A later failure is never reported when an earlier
one is observable. REMOTE_UNINITIALIZED is a stage-1 stop, never a license to
use the sibling as a remote substitute.

## Lifecycle, preconditions, idempotence, and leases

~~~mermaid
stateDiagram-v2
  [*] --> RemoteAbsent
  RemoteAbsent --> RemoteMaterialized: human creates initial Wiki page
  RemoteMaterialized --> Preflighted: preflight succeeds
  Preflighted --> WikiCandidateWritten: candidate Wiki write and owned checks pass
  WikiCandidateWritten --> WikiReviewed: independent review checks exact candidate
  WikiReviewed --> WikiApproved: immutable approval record is frozen
  WikiApproved --> WikiPublished: publisher consumes approval record and publishes exact candidate
  WikiPublished --> WikiReadbackApproved: Wiki semantic readback approves published identity
  WikiReadbackApproved --> ParentProjectionPrepared: sync-parent succeeds
  ParentProjectionPrepared --> ParentPinPR: parent PR opened
  ParentPinPR --> ParentPinMerged: parent PR merged
  ParentPinMerged --> MergedParentReadback: merged identity readback
  MergedParentReadback --> FreshCloneVerified: fresh recursive clone passes
  FreshCloneVerified --> CleanupReady: read-only proof passes
  CleanupReady --> SiblingAbsent: separately authorized exact deletion
  RemoteAbsent --> Stopped: no source edit
~~~

Every command requiring a record verifies its predecessor record, canonical
digest, request lineage, and exact identity. A successful repeat with identical
inputs returns idempotent, exit 0, and writes no new projection. A repeat with
changed input returns the mapped conflict. Mutating commands acquire the
exclusive lease at /tmp/wiki-publication/<request-id>/lease and include owner
PID, host, monotonic start, input digest, and expiry. A live holder returns
CONCURRENCY_BUSY. Stale leases are not silently stolen; a new request ID and
operator review are required. The lease is rechecked before every remote update,
rename, index update, and deletion.

Preconditions are:

- preflight: explicit transport and reader identities; source is a real
  directory; no source write.
- publish: successful preflight, clean source, exact approved SHA/tree, approved
  Wiki record, discovered branch, and current remote lease.
- readback: approved Wiki record, exact identity, reader availability, and
  Wiki-produced semantic readback record.
- sync-parent: successful readback, empty conflicting parent path, parent root
  inside the requested checkout, and no local projection drift.
- check: existing committed config, .gitmodules, and mode-160000 gitlink; no
  network or source path.
- cleanup-ready: current merged-parent, fresh-clone, readback, sibling
  cleanliness, and reachability evidence.
- cleanup: valid proof, fixed realpath, immediate fingerprint recheck,
  exclusive lease, and explicit destructive authority.

## Publication and Wiki readback

Symbolic preflight is:

~~~bash
git ls-remote --symref https://github.com/iwashita-nozomu/project_template.wiki.git HEAD
~~~

Exactly one refs/heads/<name> HEAD line and its matching SHA line are required.
The current expected result is REMOTE_UNINITIALIZED. A human-created first page
may produce BOOTSTRAP_SHA different from the approved source. Adoption requires
exact --force-with-lease=<BOOTSTRAP_SHA>, authority
AGENT_CANON_DESTRUCTIVE_GIT_AUTHORITY=explicit_user_approval, and nonempty
AGENT_CANON_DESTRUCTIVE_GIT_REASON. The lease is rechecked before update.

The Wiki workflow creates approval and readback records. AgentCanon readback
checks only record schema, identity/digest, and transport/reader availability.
The Wiki workflow owns all page/link coverage and may return
WIKI_READBACK_NOT_APPROVED; AgentCanon reports that record value and does not
calculate it.

wiki_publication.py is one cohesive publication tool. It is separate from
tools/sync_agent_canon.sh; that script owns only shared AgentCanon root-view
sync and is never a Wiki publication, parent-pin, or cleanup dependency.

## Parent projection and committed config

The parent config is written only after Wiki approval/readback and contains
concrete parent values, identity, and digests, never page arrays:

~~~toml
schema_version = 1

[publication]
projection = "github_wiki"
submodule_path = "wiki"
remote_url = "https://github.com/iwashita-nozomu/project_template.wiki.git"
default_branch = "<DISCOVERED_BRANCH>"
approved_sha = "05e3bb317410bcaf2db60a9df8f72154bd8f7629"
approved_tree = "891d2abf3e88d7ccdb5e488622969464abedfe21"
reader_url = "https://github.com/iwashita-nozomu/project_template/wiki"
approval_record_schema = "wiki.semantic-approval"
approval_record_version = 1
approval_record_id = "<WIKI_RECORD_ID>"
approval_record_digest = "<WIKI_RECORD_SHA256>"
page_set_digest = "<OPAQUE_WIKI_DIGEST>"
home_links_digest = "<OPAQUE_WIKI_DIGEST>"
publication_boundary = "publication-only"
~~~

Exact .gitmodules replacement rules:

1. Read current bytes and parse only existing submodule sections.
2. Preserve every section except a section whose path is exactly wiki.
3. If no wiki section exists, append one LF-terminated section. If exactly one
   exists, replace that complete section. More than one is GITMODULES_CONFLICT.
4. The replacement has exactly path = wiki, the exact transport URL, and
   branch = <DISCOVERED_BRANCH>. No local path or guessed branch is written.
5. Write same-directory temp bytes, fsync, atomically replace, fsync directory,
   then verify bytes and parsed section.

sync-parent captures config bytes, .gitmodules bytes, and prior index entry as a
transaction preimage. It validates all new bytes, writes config and .gitmodules
through same-directory temp files, updates the gitlink as one locked index
transaction, and emits success only after all postimages match. A journal
records preimage/postimage digests. Crash recovery restores the exact preimage
or completes the exact postimage; it never leaves partial success. The parent PR
is separate and this command does not commit or push.

check validates only committed parent projection: config schema, concrete
identity, .gitmodules exact section, mode 160000, gitlink SHA/tree, and parent
scope. It never parses Wiki pages or runs Wiki checks.

## Parent clone and devcontainer contract

Required merged-parent readback and fresh clone:

~~~bash
git clone --recurse-submodules https://github.com/iwashita-nozomu/project_template.git <fresh-clone>
git -C <fresh-clone>/vendor/agent-canon rev-parse HEAD
git -C <fresh-clone>/wiki rev-parse HEAD
git -C <fresh-clone> ls-tree HEAD wiki
bash <fresh-clone>/tools/ci/check_fresh_clone.sh --parent-url https://github.com/iwashita-nozomu/project_template.git --fixture <fresh-clone>/tests/fixtures/fresh-clone --expected-wiki-sha 05e3bb317410bcaf2db60a9df8f72154bd8f7629 --expected-wiki-tree 891d2abf3e88d7ccdb5e488622969464abedfe21
~~~

Existing clones may synchronize submodules, but that is not fresh-clone proof.
The parent dynamically registers initialized .gitmodules submodules, including
/workspace/wiki and /workspace/vendor/agent-canon, as safe directories. It never
registers the host sibling. Parent tests cover only this behavior and
parent-owned docs.

## Capability and owner routing contract

The exact generic catalog is vendor/agent-canon/agents/skills/catalog.yaml.
Each catalog entry is a closed object with exactly these nine keys: name,
schema_version, capability, owner, projection, source_kind, parent_projection,
entrypoint, and route_contract. Missing, extra, or unknown catalog keys are
invalid. The wiki-publication entry is:

~~~yaml
- name: wiki-publication
  schema_version: 1
  capability: publication
  owner: wiki-publication
  projection: github_wiki
  source_kind: repository-submodule
  parent_projection: template
  entrypoint: tools/agent_tools/wiki_publication.py
  route_contract: capability-owner-v1
~~~

The exact route input is a JSON file passed to:

~~~bash
python3 vendor/agent-canon/tools/agent_tools/route.py --input-json /tmp/wiki-publication/<request-id>/route-input.json --catalog vendor/agent-canon/agents/skills/catalog.yaml --format json
~~~

The normalized input is one closed JSON object with exactly six keys:
schema_version, capability, owner, projection, source_kind, and
parent_projection. schema_version is integer 1. The other five values are
nonempty lowercase strings matching [a-z0-9][a-z0-9._-]*. Selection requires
exact equality on all six fields and one unique entry. Prose prompts, Wiki
keywords, URLs, filenames, normalization aliases, and unlisted keys have zero
authority.

The route output uses the same envelope family with command=route and result
keys normalized_input, catalog_digest, candidate_names, and selected_name.
The common top-level status remains exactly ok, idempotent, or error. Route
selection state appears only inside result: selected_name is a string on one
unique match and null otherwise. There is no second top-level status enum.
Missing keys return ROUTE_INPUT_MISSING. Extra or unknown keys, wrong types,
empty values, invalid token formats, and conflicting duplicate values return
ROUTE_INPUT_INVALID. Zero matches return ROUTE_NO_MATCH; multiple matches
return ROUTE_AMBIGUOUS; duplicate catalog names or conflicting catalog fields
return ROUTE_CATALOG_CONFLICT. Every failure has status=error and exit 2. One
unique match has status=ok and exit 0. idempotent is reserved by the common
envelope and is not a route-selection outcome; there is no keyword fallback.

Positive fixtures cover exact publication and generic owner matching. Negative
fixtures cover missing capability/owner, wrong owner/projection, keyword-only
prose, two matching entries, duplicate catalog name, and a non-Wiki capability.
Each asserts the complete output envelope, normalized fields, candidate list,
status, failure, exit code, and no keyword fallback.

## Exact future paths and dependency/header matrix

These paths are future targets only. Do not activate their dependency headers in
this task. Each row is one edge; “no header” is explicit.

### AgentCanon paths

| Future/inactive path | Kind | Upstream owner file | Downstream owner/checker file | Sole owner file | Forbidden surface |
| --- | --- | --- | --- | --- | --- |
| vendor/agent-canon/documents/wiki-publication-contract.md | future/inactive design/header | vendor/agent-canon/documents/SHARED_RUNTIME_SURFACES.md | vendor/agent-canon/tools/agent_tools/wiki_publication.py | vendor/agent-canon/documents/wiki-publication-contract.md | parent URL, Wiki arrays |
| vendor/agent-canon/agents/skills/wiki-publication.md | future/inactive skill/header | vendor/agent-canon/documents/wiki-publication-contract.md | vendor/agent-canon/tools/agent_tools/wiki_publication.py | vendor/agent-canon/agents/skills/wiki-publication.md | Wiki checks |
| vendor/agent-canon/.agents/skills/wiki-publication/SKILL.md | future/inactive runtime view/header | vendor/agent-canon/agents/skills/wiki-publication.md | vendor/agent-canon/tools/agent_tools/check_agent_runtime_alignment.py | vendor/agent-canon/agents/skills/wiki-publication.md | parent config |
| vendor/agent-canon/agents/skills/catalog.yaml | future/inactive catalog/header | vendor/agent-canon/agents/skills/wiki-publication.md | vendor/agent-canon/tools/agent_tools/route.py | vendor/agent-canon/agents/skills/catalog.yaml | keyword activation |
| vendor/agent-canon/tools/catalog.yaml | future/inactive catalog/header | vendor/agent-canon/documents/wiki-publication-contract.md | vendor/agent-canon/tools/agent_tools/wiki_publication.py | vendor/agent-canon/tools/catalog.yaml | parent values |
| vendor/agent-canon/tools/agent_tools/wiki_publication.py | future/inactive tool/header | vendor/agent-canon/documents/wiki-publication-contract.md | vendor/agent-canon/tests/agent_tools/test_wiki_publication.py | vendor/agent-canon/tools/agent_tools/wiki_publication.py | page/link oracle |
| vendor/agent-canon/tools/agent_tools/route.py | future/inactive tool/header | vendor/agent-canon/agents/skills/catalog.yaml | vendor/agent-canon/tests/agent_tools/test_route.py | vendor/agent-canon/tools/agent_tools/route.py | keyword scan |
| vendor/agent-canon/tests/agent_tools/test_wiki_publication.py | future/inactive test/header | vendor/agent-canon/tools/agent_tools/wiki_publication.py | none | vendor/agent-canon/tests/agent_tools/test_wiki_publication.py | parent values |
| vendor/agent-canon/tests/agent_tools/test_route.py | future/inactive test/header | vendor/agent-canon/tools/agent_tools/route.py | none | vendor/agent-canon/tests/agent_tools/test_route.py | prose oracle |
| vendor/agent-canon/documents/repo-structure-contract.toml | future/inactive manifest/header | vendor/agent-canon/documents/SHARED_RUNTIME_SURFACES.md | vendor/agent-canon/tools/agent_tools/repo_structure_contract.py | vendor/agent-canon/documents/repo-structure-contract.toml | Wiki semantics |
| vendor/agent-canon/tools/agent_tools/repo_structure_contract.py | future/inactive tool/header | vendor/agent-canon/documents/repo-structure-contract.toml | vendor/agent-canon/tests/agent_tools/test_repo_structure_contract.py | vendor/agent-canon/tools/agent_tools/repo_structure_contract.py | parent paths |
| vendor/agent-canon/tests/agent_tools/test_repo_structure_contract.py | future/inactive test/header | vendor/agent-canon/tools/agent_tools/repo_structure_contract.py | none | vendor/agent-canon/tests/agent_tools/test_repo_structure_contract.py | Wiki content |
| vendor/agent-canon/CONTAINER_OPERATIONS.md | future/inactive shared contract/header | vendor/agent-canon/documents/SHARED_RUNTIME_SURFACES.md | docker/register_safe_directories.sh | vendor/agent-canon/CONTAINER_OPERATIONS.md | sibling safe directory |
| vendor/agent-canon/tests/fixtures/wiki-publication-route/ | future/inactive fixture directory/no header | vendor/agent-canon/tests/agent_tools/test_route.py | none | vendor/agent-canon/tests/agent_tools/test_route.py | production route input |

### Parent paths

| Future/inactive path | Kind | Upstream owner file | Downstream owner/checker file | Sole owner file | Forbidden surface |
| --- | --- | --- | --- | --- | --- |
| documents/wiki-publication.toml | future/inactive config/header | documents/wiki-submodule-publication-design.md | vendor/agent-canon/tools/agent_tools/wiki_publication.py | documents/wiki-publication.toml | page arrays, sibling |
| .gitmodules | future/inactive Git metadata/no header | documents/wiki-submodule-publication-design.md | tools/ci/check_fresh_clone.sh | .gitmodules | guessed branch |
| wiki | future/inactive mode-160000 gitlink/no header | .gitmodules | tools/ci/check_fresh_clone.sh | .gitmodules | parent content |
| wiki/Home.md | future/inactive remote-owned readback/no header | documents/wiki-submodule-publication-design.md | README.md | wiki/Home.md | parent staged edit |
| wiki/Reports-and-Evidence.md | future/inactive remote-owned readback/no header | documents/wiki-submodule-publication-design.md | README.md | wiki/Reports-and-Evidence.md | raw-evidence copy |
| responsibility-scope.toml | future/inactive manifest/header | documents/wiki-submodule-publication-design.md | vendor/agent-canon/tools/agent_tools/responsibility_scope.py | responsibility-scope.toml | Wiki semantics |
| README.md | future/inactive parent doc/header | documents/README.md | none | README.md | Wiki review |
| QUICK_START.md | future/inactive parent doc/header | documents/template-bootstrap.md | none | QUICK_START.md | Wiki navigation |
| documents/README.md | future/inactive parent doc/header | documents/wiki-submodule-publication-design.md | README.md | documents/README.md | raw-report canon |
| documents/template-github-remote.md | future/inactive parent contract/header | documents/wiki-submodule-publication-design.md | documents/wiki-publication.toml | documents/template-github-remote.md | Wiki semantics |
| documents/template-bootstrap.md | future/inactive parent contract/header | documents/wiki-submodule-publication-design.md | tools/ci/check_fresh_clone.sh | documents/template-bootstrap.md | sibling substitution |
| documents/repository-audit-checklist.md | future/inactive parent doc/header | responsibility-scope.toml | none | documents/repository-audit-checklist.md | Wiki approval |
| docker/register_safe_directories.sh | future/inactive parent tool/header | vendor/agent-canon/CONTAINER_OPERATIONS.md | tests/tools/test_container_config.py | docker/register_safe_directories.sh | host sibling |
| docker/packs/default.toml | future/inactive parent config/header | vendor/agent-canon/CONTAINER_OPERATIONS.md | docker/README.md | docker/packs/default.toml | policy drift |
| docker/README.md | future/inactive parent doc/header | docker/packs/default.toml | none | docker/README.md | Wiki checks |
| tests/tools/test_container_config.py | future/inactive parent test/header | docker/register_safe_directories.sh | none | tests/tools/test_container_config.py | Wiki semantics |
| tools/ci/check_fresh_clone.sh | future/inactive parent tool/header | .gitmodules | tests/fixtures/fresh-clone/README.md | tools/ci/check_fresh_clone.sh | mutable clone |
| tools/ci/check_fresh_clone.sh | future/inactive parent tool/header | documents/wiki-publication.toml | tests/fixtures/fresh-clone/README.md | tools/ci/check_fresh_clone.sh | mutable clone |
| tests/fixtures/fresh-clone/ | future/inactive fixture directory/no header | tools/ci/check_fresh_clone.sh | none | tools/ci/check_fresh_clone.sh | runtime source |

These are exact path-level design edges, not active headers. No future header is activated until
its path exists and owner review approves it. Fixture directories and
remote-owned files deliberately have no header.

## Cleanup safety proof and exact deletion transition

cleanup-ready is read-only and emits schema wiki.cleanup-proof, version 1:

~~~json
{
  "schema": "wiki.cleanup-proof",
  "schema_version": 1,
  "proof_id": "<UUID>",
  "allowlist": ["/mnt/l/workspace/project_template.wiki"],
  "requested_path": "/mnt/l/workspace/project_template.wiki",
  "realpath": "/mnt/l/workspace/project_template.wiki",
  "filesystem": {"st_dev": 0, "st_ino": 0, "is_symlink": false, "is_mount": false, "is_device": false, "mode": "directory"},
  "worktree": {"is_worktree": true, "is_detached": false, "git_dir": "<exact>", "common_dir": "<exact>", "linked_worktrees": [], "submodules": [], "alternates": []},
  "git_state": {"tracked": [], "staged": [], "unstaged": [], "untracked": [], "ignored": [], "refs": [], "reflogs": [], "stashes": []},
  "commit_closure": {"unique_commits": [], "remote_reachable": [], "remote_absent": [], "unknown": []},
  "identities": {"wiki_readback_digest": "<digest>", "merged_parent_commit": "<40 hex>", "merged_parent_gitlink": "<40 hex>", "fresh_clone_parent_commit": "<40 hex>", "fresh_clone_gitlink": "<40 hex>", "wiki_commit": "<40 hex>", "wiki_tree": "<40 hex>"},
  "fingerprint_before": "<sha256>",
  "fingerprint_recheck": "<sha256>",
  "authority": {"required": "explicit_user_approval", "granted": false, "reason": null},
  "decision": "cleanup-ready"
}
~~~

The proof algorithm is exact:

1. Require requested path and realpath to equal the single allowlisted path.
   Use lstat and directory file descriptors. Reject symlinks, mounts, block or
   character devices, FIFOs, sockets, and any special file below the root.
   Require one expected device and reject traversal.
2. Verify an ordinary Git worktree with matching git_dir/common_dir. Reject
   detached HEAD, linked worktrees, nested submodules, alternates, and
   administrative directories outside the sibling control boundary.
3. Record tracked, staged, unstaged, untracked, and ignored entries using
   porcelain-v2 status and index/worktree comparisons. Any nonempty class is
   DIRTY_OVERLAP. Record every ref, reflog, stash, and reachable object.
   Stash, reflog-only object, alternate, linked-worktree ref, submodule, or
   detached state is CLEANUP_OWNERSHIP_UNPROVED.
4. Compute the closure of HEAD, refs, index, worktree, stashes, reflogs, and
   submodule links. Compare every unique commit with Wiki readback, remote
   reachability, merged-parent pin, and fresh-clone identity. Every commit must
   be remote-reachable or remote-absent; unknown fails.
5. Require Wiki semantic readback, merged parent, and fresh clone identities to
   agree. REMOTE_UNINITIALIZED, stale, unmerged, or mismatched identities fail.
6. Create fingerprint_before from sorted relative path, lstat type/device/
   inode/mode/size/mtime, and SHA-256 content for every regular file. Write the
   proof atomically. cleanup-ready never grants authority or deletes.

Before deletion, cleanup acquires the exclusive lease, rereads the proof,
rechecks identities and every fingerprint immediately, and requires equality.
Any TOCTOU change returns CLEANUP_FINGERPRINT_CHANGED and deletes nothing. The
operator must provide:

~~~text
AGENT_CANON_DESTRUCTIVE_GIT_AUTHORITY=explicit_user_approval
AGENT_CANON_DESTRUCTIVE_GIT_REASON=<nonempty reason>
--confirm-realpath /mnt/l/workspace/project_template.wiki
~~~

The proof alone is insufficient. cleanup deletes only the exact allowlisted
directory using directory-fd, no-follow, one-filesystem operations, then verifies
absence of that exact realpath. It accepts no parent, glob, symlink, mountpoint,
device, worktree path, or sibling list. There is no compatibility phase.

## Design side-effect map

| Decision | Exact implementation/doc/workflow/config/user/test surface | Symbol/subcommand/key | Stage owner | Review gate | Validation oracle | Reuse precedent | Forbidden |
| --- | --- | --- | --- | --- | --- | --- | --- |
| One final gitlink | tool; parent config; .gitmodules; wiki; clone docs/tests | sync-parent, check, submodule_path | AgentCanon then Parent | design and pin review | transaction postimage and ls-tree | submodule precedent | local/unreachable gitlink |
| Wiki semantic sole gate | Wiki workflow; approval/readback records | approval_record_digest | Wiki | Wiki approval | Wiki check run and digest | Wiki checks | AgentCanon/parent page parsing |
| Generic record contract | future contract/tool/tests | envelope v1, record_sha256 | AgentCanon | AgentCanon review | canonical JSON and digest | record conventions | parent values |
| Preflight before source edit | Wiki runbook and tool | preflight, DEFAULT_BRANCH | Wiki/operator | preflight gate | symbolic HEAD | remote contract | guessed branch |
| Atomic projection | tool, config, .gitmodules, index journal | sync-parent, transaction.json | Parent | pin review | pre/postimage and recovery | index lock | partial success |
| Capability routing | catalog, route tool, route tests | capability, owner, projection | AgentCanon | route review | structured fixtures | catalog router | Wiki keywords |
| Fresh clone | clone tool, fixture, container tests | SHA/tree keys | Parent | pin review | fresh recursive clone | bootstrap contract | current clone proof |
| Cleanup | tool, proof, operator procedure | cleanup-ready, cleanup | Operator | destructive gate | fingerprint and reachability | guarded deletion | implicit/broad delete |
| Sibling preservation | source packet and proof | exact three paths | Design/operator | structure/flow review | forbidden-path tests | scope discipline | sibling write/broad read |

## Design-to-implementation trace

| Requirement | Exact future surface/symbol | Prompt/config/manifest impact | Owner stage | Review gate | Test oracle | Precedent | Forbidden |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Target-state-first | this design and packet target sections | prompt cites state before commands | Design | structure review | stage-order fixture | structure-refactor | edit-first |
| Remote materialization | tool preflight and Wiki runbook | run-local preflight record | Wiki | preflight | REMOTE_UNINITIALIZED/single branch | remote contract | edit before preflight |
| Wiki approval | Wiki producer and semantic records | parent stores identity/digest only | Wiki | Wiki approval | rejected/approved pass-through | Wiki checks | semantic AgentCanon |
| Generic transport | future tool and envelope | future contract document | AgentCanon | source review | all command/failure rows | record conventions | parent code |
| Parent projection | sync-parent/config/.gitmodules/gitlink | parent keys in config section | Parent | pin review | atomic transaction/mode 160000 | submodule precedent | arrays in config |
| Merged readback | merged-parent evidence | exact run-local record | Parent | merged gate | commit/gitlink equality | clone contract | local unmerged proof |
| Routing | catalog and route CLI | structured input only | AgentCanon | route review | positive/negative fixtures | catalog routing | keyword matching |
| Cleanup | cleanup-ready/cleanup/proof | authority env and proof digest | Operator | destructive gate | ref/reflog/TOCTOU | guarded cleanup | proof-triggered delete |
| Current boundary | design and packet only | no future headers now | Design | terminal reviews | two-file diff/status | scope discipline | other-path edits |

## Focused test oracle

Every future focused test asserts the envelope, exact status/exit, record-write
set, and forbidden-write set:

| Test class | Input/transition | Expected result |
| --- | --- | --- |
| Envelope | every command with valid UUID | one envelope, exact keys, exit 0 |
| Arguments | missing/extra/forbidden argument | INVALID_ARGUMENTS exit 2, no non-record write |
| Records | identical duplicate | idempotent exit 0, no overwrite |
| Records | changed duplicate | REQUEST_ID_REUSE_CONFLICT exit 2 |
| Preflight | absent remote | REMOTE_UNINITIALIZED exit 10, preflight record only |
| Preflight | auth/URL/reader mismatch | 11/12, no source or parent write |
| Preflight | zero/two symbolic branches | DEFAULT_BRANCH_UNRESOLVED exit 13 |
| Publish | dirty or wrong identity | SOURCE_DIRTY 18 or APPROVED_IDENTITY_MISMATCH 15 |
| Publish | bootstrap mismatch without authority | BOOTSTRAP_DIVERGED exit 14 |
| Publish | stale lease | LEASE_LOST exit 3, no remote update |
| Approval | malformed/changed/digest mismatch | 16/17, no semantic recomputation |
| Approval | Wiki not approved | WIKI_APPROVAL_NOT_APPROVED exit 20 |
| Readback | transport or identity change | 11/12/19, no page parsing |
| Readback | Wiki readback rejected | WIKI_READBACK_NOT_APPROVED exit 20 |
| Sync | missing record/conflicting path/drift | 30/31, preimage preserved |
| Sync | injected config/.gitmodules/index failure | ATOMIC_TRANSACTION_FAILED exit 50, full rollback |
| Sync | identical repeat | idempotent exit 0, no rewrite |
| Check | config/gitmodules/gitlink mismatch | exact 30/31 failure |
| Parent flow | unmerged or wrong merged identity | PARENT_READBACK_FAILED exit 32 |
| Clone flow | missing recursive Wiki/wrong tree | FRESH_CLONE_FAILED exit 32 |
| Route | one unique match; no match; ambiguity; catalog conflict | One match: top-level status=ok, result.selected_name is a string, exit 0. No match: status=error, result.selected_name=null, ROUTE_NO_MATCH, exit 2. Ambiguity: status=error, result.selected_name=null, ROUTE_AMBIGUOUS, exit 2. Catalog conflict: status=error, result.selected_name=null, ROUTE_CATALOG_CONFLICT, exit 2. No keyword fallback. |
| Scope | each forbidden sibling path | PATH_SCOPE_VIOLATION exit 4, zero access |
| Cleanup | dirty/staged/untracked/ignored/reflog/stash/alternate/submodule | 40/41, no deletion |
| Cleanup | symlink/mount/device/inode/worktree/detached | 4/41, no deletion |
| Cleanup | unknown unique commit or identity mismatch | CLEANUP_OWNERSHIP_UNPROVED exit 41 |
| Cleanup | changed fingerprint | CLEANUP_FINGERPRINT_CHANGED exit 41, no deletion |
| Cleanup | missing authority/empty reason | DESTRUCTIVE_AUTHORITY_REQUIRED exit 42 |
| Cleanup | valid authority and unchanged path | one exact deletion, exit 0, no other path |

## Validation, source packet, and handoff

| Gate | Owner | Required result |
| --- | --- | --- |
| Active dependency headers | Design workflow | Existing paths only, one edge per line, no future header |
| Structure | Independent structure reviewer | Target state, stage order, ownership, matrix, migration complete |
| Document flow | Independent document-flow reviewer | Stage map and reader flow unambiguous and identical in packet |
| Detailed design | Independent detailed-design reviewer | Typed contracts and oracles directly implementable |
| Scope | Parent session | Only the two allowed files differ; no formatter or Git mutation |

The future worker reads this design, exact parent owner surfaces named in the
matrix, and only these sibling files:

~~~text
/mnt/l/workspace/project_template.wiki/Home.md
/mnt/l/workspace/project_template.wiki/Reports-and-Evidence.md
/mnt/l/workspace/project_template.wiki/wiki-coverage.json
~~~

Current artifacts are this design, the noncanonical packet, and the two review
handbacks in /tmp. Future records are absent until their producer commands
create /tmp/wiki-publication/<request-id>/. The remote is currently
REMOTE_UNINITIALIZED; future source, publication, pin, merge, clone, and
cleanup artifacts are blocked and must not be inferred from the sibling.

This design and the packet are one bounded responsibility unit. REVISE edits
these same two files. Terminal APPROVE ends the task. No remote polling,
publication, source implementation, pinning, cleanup, commit, or sibling
deletion belongs to this repair.
