# Template validation contract

The repository owns its normal validation entry points:

- `make runtime-independence-check` rejects gitlinks, producer-runtime projections, updater/dispatcher references, and non-regular seed files.
- `make docs-check` verifies reader-facing local links.
- `make github-workflow-check` verifies workflow ownership and required check names.
- `make cpp-test` builds and runs the native CTest surface.
- `make test` runs focused repository tooling tests.
- `make pr-check` composes the pull-request gate.
- `make fresh-clone-check` creates, commits, publishes, and normally clones a generated descendant before rerunning project-owned checks.

The fresh-clone check starts from a clean committed tree. It uses a temporary local bare remote so it can prove ordinary clone behavior without network, credentials, recursive options, or access to the original template checkout. Docker execution is enabled explicitly with `TEMPLATE_FRESH_CLONE_RUN_DOCKER=1`.
