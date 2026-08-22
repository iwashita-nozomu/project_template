# Quick start

## 1. Clone normally

```bash
git clone <template-url> my-project
cd my-project
```

A normal clone contains only project-owned source. Project bootstrap, build,
tests, documentation, Docker, and CI do not require AgentCanon, a submodule, a
source checkout, or network access.

## 2. Preview and initialize the project

```bash
bash scripts/start_repository.sh \
  --project-slug my-project \
  --display-name "My Project" \
  --dry-run

bash scripts/start_repository.sh \
  --project-slug my-project \
  --display-name "My Project"
```

Initialization is local and offline. It does not fetch or initialize another
repository, and it writes only the project identity files.

## 3. Commit and validate

```bash
git diff --check
git add --all
git commit -m "Initialize my-project"
make pr-check
make fresh-clone-check
```

`make fresh-clone-check` requires a clean committed tree because it validates exactly what another user receives from an ordinary, non-recursive clone.

## 4. Use AgentCanon only when the task needs it

Keep the parent project source-free. Clone AgentCanon into the ignored,
task-qualified workspace and use its standalone bootstrap:

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

The AgentCanon runtime is for AgentCanon tools and skills. Run project tests
with the project's own `docker/Dockerfile` and test runner; never mount the
parent `tests/` directory into AgentCanon. Collect and publish AgentCanon evals
only through its external runtime spool and `agent-canon-log` archive. After
merged-main readback, return to the project root and run
`scripts/agent-canon-develop.sh cleanup "$TASK"` to uninstall and remove the
exact task resources.

## 5. Use Docker

```bash
docker build -f docker/Dockerfile -t project-template .
docker run --rm project-template test/testrunner.sh
```

For the repository checks:

```bash
make docker-check
make docker-test
```
