# Project Template

A starting point for Python, C++, documents, experiments, and containerized
project development. The repository is source-free with respect to AgentCanon:
it owns product code, project Docker images, tests, documents, and CI only.

A normal clone contains every project-owned file required to bootstrap, build,
test, and validate the project. It does not contain an AgentCanon submodule,
vendor checkout, source projection, or Codex runtime state.

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
project metadata and reader-facing examples only. It does not acquire or
initialize AgentCanon and does not write outside the project checkout.

After committing the initialized tree, run the descendant acceptance check:

```bash
bash tools/check_fresh_clone.sh
```

This publishes the generated repository to a temporary local bare remote, clones it normally without recursive options, hides the template source, and reruns project-owned checks.

## Use AgentCanon with Codex

AgentCanon is a separate tool and policy repository. When a task needs its
skills, hooks, or analysis tools, create a qualified, ignored development clone
under this repository's workspace and run the standalone bootstrap there:

```bash
ROOT="$PWD"
TASK="<qualified-task>"
DEV="$ROOT/workspace/agent-canondevelop/$TASK"
scripts/agent-canon-develop.sh clone "$TASK"
cd "$DEV/agent-canon"
RUNTIME="$ROOT/workspace/agent-canon-runtime/$TASK"
COMMON=(--control-parent-root "$ROOT" --runtime-root "$RUNTIME")
./bootstrap.sh "${COMMON[@]}" install
./bootstrap.sh "${COMMON[@]}" start
./bootstrap.sh "${COMMON[@]}" target add --root "$ROOT" --mode read-only
./bootstrap.sh "${COMMON[@]}" codex prepare
./bootstrap.sh "${COMMON[@]}" codex launch --project-root "$ROOT"
```

The project remains the owner of its own Docker/test runner. Do not mount
`test/`, project build state, or project credentials into the AgentCanon tool
runtime. AgentCanon's `eval collect` may read the explicitly registered project
target, and `eval sync` publishes only to the separate
[`agent-canon-log`](https://github.com/iwashita-nozomu/agent-canon-log) archive.
When the task is complete, return to the project root and run
`scripts/agent-canon-develop.sh cleanup "$TASK"`. It verifies merged-main and
clean-checkout state, uninstalls the exact runtime, and removes only the
task-qualified clone/runtime paths. Finally verify that the project worktree is
clean.

## Canonical checks

```bash
bash test/testrunner.sh
bash tools/check_fresh_clone.sh
cmake --preset dev
cmake --build --preset dev --parallel
ctest --preset dev
```

`test/testlist.toml` owns the complete static, tooling, and C++ validation list.
No project check initializes or loads AgentCanon. Docker uses the same test
entry with the tracked Dockerfile:

```bash
bash docker/run-tests.sh --tag project-template:test
```

The source tree and its parent test list are copied into the image at build
time. The Docker wrapper runs the list's `static` phase on the Host, then its
`portable` phase in the image, so Git-bound checks are not duplicated or run
against a snapshot without `.git`. The workflow has no workspace mount,
interactive development-container lifecycle, or post-create setup.

The single image is a bounded Ubuntu 24.04 test image. It intentionally omits
scientific Python, notebook, CUDA, GPU, and general developer-tool profiles;
descendant repositories add only the product dependencies they actually need.

## Repository layout

```text
.
├── AGENTS.md                  # parent project instructions
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
└── workspace/agent-canondevelop/ # ignored, temporary AgentCanon edit clones
```

See `QUICK_START.md`, `documents/contracts/template-bootstrap.md`, and
`documents/contracts/template-validation.md` for the operational contracts.
