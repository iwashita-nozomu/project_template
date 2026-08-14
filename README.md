# Project Template

A self-contained starting point for Python, C++, documents, experiments, and containerized development.

A normal clone contains every tracked file required to read, bootstrap, build, and validate the project. The default path has no submodule, no runtime checkout, no source resolver, no updater, and no upstream credential requirement.

## Start a repository

```bash
git clone <template-url> my-project
cd my-project
bash scripts/start_repository.sh \
  --project-slug my-project \
  --display-name "My Project"
git diff --check
git add --all
git commit -m "Initialize my-project"
make pr-check
```

The initializer is an offline, repository-local identity conversion. It rewrites project metadata and reader-facing examples only. It does not fetch or regenerate the static seed.

After committing the initialized tree, run the descendant acceptance check:

```bash
make fresh-clone-check
```

This publishes the generated repository to a temporary local bare remote, clones it normally without recursive options, hides the template source, and reruns project-owned checks.

## Canonical checks

```bash
make runtime-independence-check
make docs-check
make github-workflow-check
make cpp-test
make test
make pr-check
```

`make ci` is the full project-owned host gate. Docker checks use the same tracked Dockerfile:

```bash
make docker-check
make docker-build-check
make docker-run ARGS='python3 --version'
```

The default image is CPU-only. GPU support remains an explicit Docker target and requires a compatible host driver.

## Static Codex seed

`.codex/config.toml` and `.codex/agents/*.toml` are regular tracked files. `agent-canon-static-seed.json` records the producer repository and immutable source revision. The checker derives the exact role-file closure from `.codex/config.toml`. The snapshot supplies configuration data only; it does not include producer tooling, source resolvers, update state, hooks, secrets, symlinks, or network behavior.

Seed refresh is a one-way template-maintainer operation. A generated repository never checks for a newer producer revision and never updates the snapshot in the background.

## Repository layout

```text
.
├── AGENTS.md
├── .codex/                     # regular static configuration files
├── cpp/                        # C++ project and CTest targets
├── python/                     # Python package source
├── experiments/                # project experiments
├── documents/                  # project-owned contracts and design
├── docker/                     # canonical image definition and checks
├── .devcontainer/              # Dockerfile selector and read-only validation hook
├── scripts/                    # offline repository initialization
├── tools/                      # project-owned validation tools
└── tests/                      # project-owned tests
```

See `QUICK_START.md`, `documents/contracts/template-bootstrap.md`, and `documents/contracts/template-validation.md` for the operational contracts.
