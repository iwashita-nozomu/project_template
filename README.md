# Project Template

A starting point for Python, C++, documents, experiments, and containerized
project development. It owns product code, project Docker images, tests,
documents, and CI only.

A normal clone contains every project-owned file required to bootstrap, build,
test, and validate the project. It does not contain external tool checkouts,
source projections, or runtime state.

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
bash test/testrunner.sh
```

The initializer is an offline, repository-local identity conversion. It rewrites
project metadata and reader-facing examples only. It does not acquire another
repository or write outside the project checkout.

After committing the initialized tree, run the descendant acceptance check:

```bash
bash tools/check_fresh_clone.sh
```

This publishes the generated repository to a temporary local bare remote, clones it normally without recursive options, hides the template source, and reruns project-owned checks.

## Canonical checks

```bash
bash test/testrunner.sh
bash tools/check_fresh_clone.sh
cmake --preset dev
cmake --build --preset dev --parallel
ctest --preset dev
```

`test/testlist.toml` owns the complete static, tooling, and C++ validation list.
Docker uses the same test entry with the tracked Dockerfile:

```bash
bash docker/run-tests.sh --tag project-template:test
```

The source tree and its test list are copied into the image at build time. The
Docker wrapper runs the complete `all` phase inside that disposable image, so
no test command receives write capability to the caller checkout. Static and
portable classifications remain in the canonical list for direct focused use;
the Docker path has no workspace mount, interactive development-container
lifecycle, or post-create setup.

The single image is a bounded Ubuntu 24.04 test image. It intentionally omits
scientific Python, notebook, CUDA, GPU, and general developer-tool profiles;
descendant repositories add only the product dependencies they actually need.

## Repository layout

```text
.
├── AGENTS.md                  # project instructions
├── CMakeLists.txt            # root C++ project entrypoint
├── include/                  # public C++ headers
├── src/                      # production C++ sources
├── python/                   # Python package source
├── experiments/              # project experiments
├── documents/                # project contracts, design, notes, and sources
├── docker/                   # canonical image definition and checks
├── scripts/                  # offline repository initialization
├── tools/                    # project-owned validation tools
├── test/                     # runner, test list, tooling tests, and CTest sources
├── vendor/                   # empty placeholder for project-owned third-party sources
└── workspace/                # ignored project scratch space
```

See `QUICK_START.md`, `documents/contracts/template-bootstrap.md`, and
`documents/contracts/template-validation.md` for the operational contracts.
