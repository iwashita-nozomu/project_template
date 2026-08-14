# Template bootstrap contract

## Goal

A normal clone of `project-template` is a complete repository. Bootstrap changes only project identity and reader-facing examples. It must not fetch another source tree, initialize a submodule, resolve a producer checkout, read credentials, or mutate the static `.codex` seed.

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

The static seed provenance is historical input, not synchronization state. Updating it is a deliberate template-maintainer change outside descendant bootstrap.
