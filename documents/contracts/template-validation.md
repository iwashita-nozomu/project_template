# Template validation contract

The repository owns its normal validation entry points:

- `make runtime-independence-check` accepts either no AgentCanon registration or the exact inert registration, and rejects partial metadata, alternate path/URL/branch, any additional gitlink, producer-runtime projection, tracked `.agent-canon/` state, updater/dispatcher reference, or non-regular seed file.
- `make docs-check` verifies reader-facing local links.
- `make github-workflow-check` verifies workflow ownership and required check names.
- `make cpp-test` builds and runs the native CTest surface.
- `make test` runs focused repository tooling tests.
- `make pr-check` composes the pull-request gate.
- `make fresh-clone-check` creates, commits, publishes, and normally clones a generated descendant before rerunning project-owned checks.

The exact inert registration is the regular `.gitmodules` file with path `vendor/agent-canon`, URL `https://github.com/iwashita-nozomu/agent-canon.git`, and branch `main`, plus the sole mode-`160000` gitlink at that path. A checkout is not required; when one exists, its `HEAD` must equal the staged gitlink. An uninitialized checkout path must be absent or empty.

The fresh-clone check starts from a clean committed tree. It records the admitted registration state before bootstrap, uses a temporary local bare remote, and proves that initialization, publication, and an ordinary clone preserve that state exactly. Project checks run without recursive options, AgentCanon checkout initialization, network, credentials, or access to the original template checkout. Docker execution is enabled explicitly with `TEMPLATE_FRESH_CLONE_RUN_DOCKER=1`.
