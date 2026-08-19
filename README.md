# Project Template

A starting point for Python, C++, documents, experiments, containerized development, and an explicitly activated AgentCanon Codex runtime.

A normal clone contains every project-owned file required to bootstrap, build, test, and validate the project. The repository also records one exact AgentCanon submodule pin and five lexical root views. Normal project checks validate those identities without initializing the checkout or contacting an upstream service.

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

The initializer is an offline, repository-local identity conversion. It rewrites project metadata and reader-facing examples only. It preserves the AgentCanon registration, gitlink, and live-view symlinks without initializing or modifying the checkout.

After committing the initialized tree, run the descendant acceptance check:

```bash
make fresh-clone-check
```

This publishes the generated repository to a temporary local bare remote, clones it normally without recursive options, hides the template source, and reruns project-owned checks.

## Activate AgentCanon for Codex

The tracked `.codex` entries are symlink views into the exact `vendor/agent-canon` pin. Before starting a Codex session that must load AgentCanon custom agents or hooks, initialize that reviewed pin explicitly:

```bash
git submodule update --init --checkout -- vendor/agent-canon
git -C vendor/agent-canon rev-parse HEAD
git ls-files -s vendor/agent-canon
```

The two object IDs must match. This activation is deliberate user action; bootstrap, CI, Docker, `make pr-check`, and `make fresh-clone-check` do not run it automatically.

The live Codex view is exactly:

```text
AGENTS.md          -> vendor/agent-canon/ROOT_AGENTS.md
.codex/config.toml -> ../vendor/agent-canon/.codex/config.toml
.codex/agents      -> ../vendor/agent-canon/.codex/agents
.codex/hooks.json  -> ../vendor/agent-canon/.codex/hooks.json
.codex/hooks       -> ../vendor/agent-canon/.codex/hooks
```

Agent definitions, model and reasoning settings, developer instructions, and hook code remain owned by AgentCanon. The template tracks only the exact pin and view edges. It does not copy those files, import snapshots, project `tools/agent-canon`, or mirror AgentCanon tests and fixtures.

## Canonical checks

```bash
make runtime-independence-check
make docs-check
make github-workflow-check
make cpp-test
make test
make pr-check
```

`make runtime-independence-check` validates the exact submodule registration, sole gitlink, symlink modes, and lexical targets. It succeeds with an uninitialized checkout. If the checkout is initialized, it additionally requires its `HEAD` to equal the staged gitlink.

`make ci` is the full project-owned host gate. Docker checks use the same tracked Dockerfile:

```bash
make docker-check
make docker-build-check
make docker-run ARGS='python3 --version'
```

The default image is CPU-only. GPU support remains an explicit Docker target and requires a compatible host driver.

## Repository layout

```text
.
├── AGENTS.md                  # symlink to exact AgentCanon root instructions
├── .gitmodules               # exact AgentCanon source registration
├── .codex/                   # symlink views for config, agents, and hooks
├── cpp/                      # C++ project and CTest targets
├── python/                   # Python package source
├── experiments/              # project experiments
├── documents/                # project contracts, design, notes, and sources
├── docker/                   # canonical image definition and checks
├── .devcontainer/            # Dockerfile selector and read-only validation hook
├── scripts/                  # offline repository initialization
├── tools/                    # project-owned validation tools
├── tests/                    # project-owned tests
└── vendor/agent-canon         # exact gitlink; uninitialized by normal checks
```

See `QUICK_START.md`, `documents/contracts/template-bootstrap.md`, and `documents/contracts/template-validation.md` for the operational contracts.
