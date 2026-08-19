# Legacy Live AgentCanon Descendant Migration

## Scope

This contract applies only to repositories created from this Template before the live AgentCanon runtime was removed by project_template#168. Those repositories may still contain a `vendor/agent-canon` gitlink, `.gitmodules`, root-view symlinks, consumer update state, and `agent-canon-update` commands.

Current Template descendants are different: they carry an audited static seed as regular files and may retain one exact AgentCanon gitlink as inactive source identity. They do not require that checkout, an updater, network credential, publication receipt, or synchronization state for normal clone, bootstrap, build, test, documentation, or CI. This legacy procedure must not be added to the current default path.

## Why the legacy route can stop permanently

The old parent update route required an accepted transaction marker, QueueReceipt, DependencyFrontier, and G4 receipt before changing the parent projection. The AgentCanon parent front door did not consume the source-publication packet before checking those derived records, while its fresh-clone fixture pre-populated the derived records from another namespace. An empty real parent namespace could therefore fail closed even when its current pin and root views were internally consistent.

AgentCanon issue [#724](https://github.com/iwashita-nozomu/agent-canon/issues/724) owns the source-publication packet to parent-front-door repair. This Template does not own or duplicate that state machine.

## Non-negotiable safety rules

A legacy descendant migration must preserve repository-owned product, design, workflow, and operational differences. Do not re-run Template initialization over an established repository and do not replace the repository tree with the current Template tree.

The following are prohibited:

- manually fast-forwarding or staging the `vendor/agent-canon` gitlink to bypass the canonical gate;
- fabricating, editing, or copying transaction markers, QueueReceipts, DependencyFrontiers, or G4 receipts between namespaces;
- overwriting root views before classifying descendant-owned changes;
- adding a second updater, compatibility state machine, background updater, or AgentCanon runtime package to the descendant;
- treating the current Template as a source tree that can be merged wholesale into an established descendant.

## Choose one route

### Route A: temporarily retain the live runtime

Use this route only when the repository still needs a live AgentCanon source checkout before a permanent migration can be reviewed.

1. Record the staged gitlink identity, submodule `HEAD`, submodule branch/upstream, root-view targets, and `git status --short --untracked-files=all` for both parent and submodule.
2. Preserve any descendant-owned root-view or AgentCanon-source differences on a named issue branch. Do not move them into generated receipts or untracked backup directories.
3. Upgrade the AgentCanon source implementation that contains the fix for AgentCanon #724 without changing the parent gitlink by hand.
4. Require the source-publication owner to hand off one valid `source-publication-ready.json` into the parent-owned `.agent-canon/update-lifecycle/state/` namespace.
5. Run only the canonical AgentCanon front door with the required explicit Git and commit-provenance authority. The front door must validate remote `main` commit/tree readback, materialize QueueReceipt, pending/accepted DependencyFrontier, transaction marker, and G4, and then apply the parent projection.
6. Verify that a second invocation is identity-preserving and that no receipt was copied from another namespace.

This route is a bounded compatibility operation. It does not make live AgentCanon runtime integration part of the current Template contract.

### Route B: migrate permanently to the static-seed default

This is the preferred long-term route for descendants that do not need to develop AgentCanon itself.

1. **Create a reviewable migration branch.** Start from the descendant's latest main and include the tracking issue number in the branch name.
2. **Inventory ownership before deletion.** Classify every tracked path reached through `.gitmodules`, `vendor/agent-canon`, `AGENTS.md`, `.codex/**`, `tools/agent-canon`, `.agent-canon/**`, AgentCanon workflows, and update targets as one of:
   - descendant-owned product or policy;
   - audited static seed still required by the descendant;
   - live-runtime transport, projection, generated state, or producer-only maintenance surface.
3. **Freeze descendant-owned differences.** Convert required descendant-owned content into regular files under its canonical local owner. Preserve semantic changes; do not preserve an obsolete symlink merely to retain its bytes.
4. **Select an audited seed.** Use an explicit AgentCanon source commit and an allowlisted static-seed manifest. Import only the files needed by the descendant as regular files, and retain immutable provenance equivalent to `agent-canon-static-seed.json`. Do not copy the AgentCanon source tree or its updater.
5. **Remove live execution atomically.** In one reviewable migration series, remove `tools/agent-canon`, consumer updater/latest/sync targets, checkout secrets, root projection symlinks, tracked `.agent-canon/**` state, and update-lifecycle runtime state that no longer has an owner. Select one source-identity state: remove `.gitmodules` and every gitlink together, or normalize them to the exact AgentCanon registration and sole mode-`160000` `vendor/agent-canon` gitlink. Never leave partial metadata, an alternate URL/path/branch, or an additional gitlink.
6. **Restore project-owned commands.** Normal test, CI, docs, workflow, Docker, and bootstrap commands must resolve only to descendant-owned tools and dependencies.
7. **Verify a checkout-independent clone.** Clone the migrated repository normally, without recursive submodules, AgentCanon credentials, or an initialized AgentCanon checkout. Verify that the selected registration state is preserved exactly, then run the descendant's canonical host checks and container build/run checks.
8. **Keep rollback commit-addressable.** Separate ownership-preservation changes from live-runtime removal when that improves reviewability. Roll back by reverting reviewed commits, never by restoring untracked receipt directories.

## Required evidence

A completed permanent migration records all of the following:

```text
git ls-files -s .gitmodules vendor/agent-canon
# either no output, or .gitmodules is regular and vendor/agent-canon is the sole mode 160000 entry

git ls-files -s AGENTS.md .codex agent-canon-static-seed.json
# required seed paths are regular tracked files, not symlinks

git grep -n -E 'vendor/agent-canon|tools/agent-canon|AGENT_CANON_READ_TOKEN|agent-canon-(update|latest|sync)'
# no default runtime path; registration contracts and historical migration documentation may mention the terms

git clone <descendant> <clean-directory>
# preserves the selected registration state and succeeds without --recurse-submodules or AgentCanon credentials
```

The repository must then pass its project-owned pull-request checks and fresh-clone acceptance. A Docker/runtime change also requires the repository's canonical cold build and runtime command.

## Responsibility boundary

AgentCanon owns source publication identity, packet validation, QueueReceipt/DependencyFrontier/G4 materialization, and safe live parent projection. The descendant owns preservation of its local design and product differences. The current Template owns the static seed, optional exact inactive registration, checkout-independent bootstrap, and runtime-independence contract. None of these owners may recreate another owner's state machine under a different name.
