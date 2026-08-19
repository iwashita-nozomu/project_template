# Template bootstrap contract

## Goal

A normal clone of `project-template` is complete for project-owned bootstrap and validation. AgentCanon source registration is an optional repository-identity layer, not an execution dependency. Bootstrap changes only project identity and reader-facing examples; it must not fetch another source tree, initialize a submodule, resolve a producer checkout, read credentials, or mutate the static `.codex` seed.

The admitted registration states are:

1. `.gitmodules` and gitlinks are absent; or
2. `.gitmodules` is a regular file with the exact `vendor/agent-canon` path, `https://github.com/iwashita-nozomu/agent-canon.git` URL, and `main` branch, and `vendor/agent-canon` is the sole mode-`160000` gitlink.

The initializer preserves the admitted state byte-for-tree: it neither creates nor removes the registration pair, does not change the pin, and does not initialize the checkout. Live AgentCanon root projections are a separate explicit integration step and are not created by descendant bootstrap.

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

The static seed provenance and an optional gitlink pin are historical source identities, not synchronization state. Updating either is a deliberate reviewed change outside descendant bootstrap.

## Maintainer-only static-seed import

Template maintainers import one fresh AgentCanon static-seed export explicitly:

```bash
python3 tools/import_agent_canon_static_seed.py --bundle <fresh-export-directory>
```

The command validates the complete export before taking the template snapshot
lock and writes only `agent-canon-static-seed.json`, `.codex/config.toml`, and
`.codex/agents/*.toml`. It reports `pass` with source revision and role
add/update/delete counts, or `noop` when the snapshot already matches. A
failed transaction restores the previous snapshot or leaves a durable
fail-closed recovery journal. Review the resulting diff and provenance before
committing it.

This is a maintainer operation, not bootstrap behavior. `start_repository.sh`,
normal validation, CI, Docker, and generated repositories do not invoke it; a
descendant never resolves a producer checkout, remote, credential, or latest
revision.
