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
make pr-check
```

The initializer is an offline, repository-local identity conversion. It rewrites
project metadata and reader-facing examples only. It does not acquire or
initialize AgentCanon and does not write outside the project checkout.

After committing the initialized tree, run the descendant acceptance check:

```bash
make fresh-clone-check
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
`tests/`, project build state, or project credentials into the AgentCanon tool
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
make docs-check
make github-workflow-check
make cpp-test
make test
make pr-check
```

`make docs-check` verifies reader-facing local links and `make pr-check`
composes the project-owned pull-request gate. No project check initializes or
loads AgentCanon.

`make ci` is the full project-owned host gate. Docker checks use the same tracked Dockerfile:

```bash
docker build -f docker/Dockerfile -t project-template .
docker run --rm project-template test/testrunner.sh
```

The source tree and its parent test list are copied into the image at build
time. The test command therefore needs no workspace mount or interactive
development-container lifecycle. The commented command contract lives in
`test/testlist.toml` and is executed by `test/testrunner.sh`.

The default image is CPU-only. GPU support remains an explicit Docker target and requires a compatible host driver.

## Repository layout

```text
.
├── AGENTS.md                  # parent project instructions
├── cpp/                      # C++ project and CTest targets
├── python/                   # Python package source
├── experiments/              # project experiments
├── documents/                # project contracts, design, notes, and sources
├── docker/                   # canonical image definition and checks
├── scripts/                  # offline repository initialization
├── tools/                    # project-owned validation tools
├── tests/                    # project-owned tests
└── workspace/agent-canondevelop/ # ignored, temporary AgentCanon edit clones
```

See `QUICK_START.md`, `documents/contracts/template-bootstrap.md`, and
`documents/contracts/template-validation.md` for the operational contracts.
