# Project Template

A self-contained starting point for Python, C++, documents, experiments, and containerized development.

A normal clone contains every project-owned file required to read, bootstrap, build, and validate the project. The repository may additionally record one exact AgentCanon submodule registration as source identity. Whether that registration is absent or present, the default path does not initialize or consume its checkout and requires no source resolver, updater, upstream credential, or network access.

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

The initializer is an offline, repository-local identity conversion. It rewrites project metadata and reader-facing examples only. It does not fetch or regenerate the static configuration, and it preserves the admitted AgentCanon registration state instead of creating, removing, or initializing it.

After committing the initialized tree, run the descendant acceptance check:

```bash
make fresh-clone-check
```

This publishes the generated repository to a temporary local bare remote, clones it normally without recursive options, hides the template source, and reruns project-owned checks. It also proves that the admitted registration state is unchanged and that any registered checkout remains uninitialized.

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

## Static Codex configuration

`.codex/config.toml` and `.codex/agents/*.toml` are regular tracked files. The repository-owned runtime-independence checker derives and validates the exact role-file closure from `.codex/config.toml`. The tracked snapshot supplies configuration data only; it contains no source resolver, updater, update state, hook, secret, symlink, or network behavior.

Normal clone, initialization, checks, CI, Docker, and generated repositories read these files directly. None of those paths initializes an admitted AgentCanon registration, performs background refresh, or requires another checkout. Replacing the tracked snapshot is an explicit template-maintainer operation documented in the repository-local [static-configuration maintenance contract](documents/design/template-static-seed-import.md); normal users do not run it.

## AgentCanon source registration

The runtime-independence contract admits exactly two repository states:

- no `.gitmodules` file and no gitlink; or
- one regular `.gitmodules` file registering path `vendor/agent-canon`, URL `https://github.com/iwashita-nozomu/agent-canon.git`, branch `main`, together with the sole mode-`160000` gitlink at that path.

The second state records source identity and a pin only. It does not authorize default checkout initialization, runtime dispatch, root-view symlinks, `notes/` or `tests/` symlinks, or tracked `.agent-canon/` state. Partial registration, alternate path or URL, and additional gitlinks fail closed.

## Repository layout

```text
.
├── AGENTS.md
├── .codex/                     # regular static configuration files
├── cpp/                        # C++ project and CTest targets
├── python/                     # Python package source
├── experiments/                # project experiments
├── documents/                  # contracts, design, notes, and source records
├── docker/                     # canonical image definition and checks
├── .devcontainer/              # Dockerfile selector and read-only validation hook
├── scripts/                    # offline repository initialization
├── tools/                      # project-owned validation tools
└── tests/                      # project-owned tests
```

When the optional source registration is present, `.gitmodules` and the `vendor/agent-canon` gitlink are added as one atomic metadata pair; they are not part of the default runtime layout.

See `QUICK_START.md`, `documents/contracts/template-bootstrap.md`, and `documents/contracts/template-validation.md` for the operational contracts.
