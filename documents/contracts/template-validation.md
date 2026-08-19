# Template validation contract

The repository owns its normal validation entry points:

- `make runtime-independence-check` validates the exact AgentCanon submodule registration, sole gitlink, five required live-view symlinks, and the absence of copied AgentCanon configuration, internal tools, producer tests, fixtures, updater state, and runtime dispatch references.
- `make docs-check` verifies reader-facing local links.
- `make github-workflow-check` verifies workflow ownership and required check names.
- `make cpp-test` builds and runs the native CTest surface.
- `make test` runs focused repository tooling tests.
- `make pr-check` composes the pull-request gate.
- `make fresh-clone-check` creates, commits, publishes, and normally clones a generated descendant before rerunning project-owned checks.

## Uninitialized-checkout validation

The runtime-independence checker reads tracked modes and lexical symlink targets. It therefore validates all of the following without initializing `vendor/agent-canon`:

- `.gitmodules` is one regular exact registration;
- `vendor/agent-canon` is the sole mode-`160000` entry;
- `AGENTS.md`, `.codex/config.toml`, `.codex/agents`, `.codex/hooks.json`, and `.codex/hooks` are mode-`120000` entries with exact targets;
- no regular `.codex/agents/*.toml`, static-seed importer/provenance, `tools/agent-canon`, AgentCanon test namespace, or copied fixture exists;
- project execution paths do not invoke AgentCanon update, checkout, source resolver, or internal tools.

When the checkout is initialized, the same checker additionally requires:

```text
vendor/agent-canon HEAD == staged vendor/agent-canon gitlink
```

A mismatch fails rather than loading an unreviewed runtime.

## Fresh-clone boundary

The fresh-clone check starts from a clean committed tree. It uses a temporary local bare remote so it can prove that the exact registration and symlink modes survive an ordinary clone while the checkout remains uninitialized. Project checks run without network, credentials, recursive options, access to the original template checkout, or dereferencing the AgentCanon views. Docker execution is enabled explicitly with `TEMPLATE_FRESH_CLONE_RUN_DOCKER=1`.

## Codex activation

Loading the AgentCanon-owned custom agents and hooks is outside the normal validation path. A user explicitly initializes the exact reviewed pin before the Codex session:

```bash
git submodule update --init --checkout -- vendor/agent-canon
make runtime-independence-check
```

No validation command advances the pin, selects latest `main`, or repairs root views from the network.
