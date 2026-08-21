# Template bootstrap contract

## Goal

A normal clone of `project-template` is complete for project-owned bootstrap and validation. It records the exact AgentCanon submodule registration, one mode-`160000` gitlink, and the bounded root symlink view without initializing that checkout.

Bootstrap changes only project identity and reader-facing examples. It must not fetch another source tree, initialize or advance the registered submodule, resolve a latest AgentCanon revision, read credentials, rewrite the root views, or copy AgentCanon configuration into regular template files.

## Preserved AgentCanon identity

The initializer preserves these tracked identities exactly:

```text
.gitmodules
vendor/agent-canon                         # sole gitlink
AGENTS.md                                  # exact symlink
.codex/config.toml                         # exact symlink
.codex/agents                              # exact symlink
.codex/hooks.json                          # exact symlink
.codex/hooks                               # exact symlink
```

The symlink targets are validated lexically, so bootstrap and normal checks do not need the checkout. Codex activation is a separate explicit operation:

```bash
git submodule update --init --checkout -- vendor/agent-canon
```

That command is never called by descendant bootstrap.

## Entry points

Preview:

```bash
bash scripts/start_repository.sh --project-slug example --display-name "Example" --dry-run
```

Apply:

```bash
bash scripts/start_repository.sh --project-slug example --display-name "Example"
```

The optional bare-repository example is `/mnt/git/template.git`; callers may replace it with their own local or hosted origin after initialization.

## State handling

The initializer refuses a dirty worktree unless `--force` is explicit. Repeating the same initialization is a no-op. Unknown options are rejected rather than silently selecting a compatibility mode.

After applying, review and commit the diff before running read-only validation:

```bash
bash scripts/start_repository.sh --validate-only
```

The initializer reports `agent_canon_view=exact_live_symlinks`. It does not own an AgentCanon snapshot, importer, update transaction, background synchronization process, or compatibility alias.

## Ownership boundary

- AgentCanon owns `ROOT_AGENTS.md`, `.codex/config.toml`, `.codex/agents/**`, `.codex/hooks.json`, `.codex/hooks/**`, and their runtime semantics.
- This repository owns the exact source registration, gitlink, symlink edges, project source/build/test/docs, and offline bootstrap.
- Project commands must not execute `vendor/agent-canon/tools/**` as an implicit dependency.
- `tools/agent-canon`, copied AgentCanon tests/fixtures, static provenance, and importer placeholders are forbidden.
