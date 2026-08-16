# Project Template

A self-contained starting point for Python, C++, documents, experiments, and
containerized development.

A normal clone contains every tracked file required to read, bootstrap, build,
and validate the project. The default path has no submodule, no runtime
checkout, no source resolver, no updater, and no upstream credential
requirement.

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
```

The initializer is an offline, repository-local identity conversion. It
rewrites project metadata and reader-facing examples only. It does not fetch or
regenerate the static configuration.

Open the repository in its Dev Container, or build target `cpu-dev`, before
running checks. The image already contains the Python environment, Node.js,
standard CLIs, CMake, and Ninja; no post-create installation runs.

```bash
export PROJECT_UID="$(id -u)"
export PROJECT_GID="$(id -g)"
code .
```

Inside the canonical environment:

```bash
make pr-check
make fresh-clone-check
```

The descendant acceptance check publishes the generated repository to a
temporary local bare remote, clones it normally without recursive options,
hides the template source, and reruns project-owned checks.

## Canonical checks

`validation/profiles.toml` maps changed paths to responsibility profiles. Pull
request CI executes only applicable profiles in the same `cpu-dev` image and
reports independent profiles as `not_applicable`, not as passing. Routing
self-changes and integration events select the full profile set.

```bash
make check-matrix
make runtime-independence-check
make docs-check
make github-workflow-check
make cpp-test
make test
make pr-check
```

Build-time full acceptance uses the same tracked Dockerfile:

```bash
make docker-build-check
```

The default development image is CPU-only. GPU support is the explicit
`gpu-dev` target and requires a compatible host driver.

## Static Codex configuration

`.codex/config.toml` and `.codex/agents/*.toml` are regular tracked files. The
repository-owned runtime-independence checker derives and validates the exact
role-file closure from `.codex/config.toml`. The tracked snapshot supplies
configuration data only; it contains no source resolver, updater, update state,
hook, secret, symlink, or network behavior.

Normal clone, initialization, checks, CI, Docker, and generated repositories
read these files directly. None of those paths performs background refresh or
requires another checkout. Replacing the tracked snapshot is an explicit
template-maintainer operation documented in the repository-local
[static-configuration maintenance contract](documents/design/template-static-seed-import.md);
normal users do not run it.

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
├── .devcontainer/              # image target, identity, and mount projection
├── validation/                 # responsibility-to-command routing source
├── scripts/                    # offline repository initialization
├── tools/                      # project-owned validation tools
└── tests/                      # project-owned tests
```

See `QUICK_START.md`, `documents/contracts/template-bootstrap.md`, and
`documents/contracts/template-validation.md` for the operational contracts.
