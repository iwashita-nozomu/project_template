# Quick start

## 1. Clone normally

```bash
git clone <template-url> my-project
cd my-project
```

A normal clone leaves `vendor/agent-canon` uninitialized. Project-owned bootstrap, build, tests, documentation, Docker, and CI still work because they validate the exact registration and lexical live views without reading the target checkout.

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

Initialization is local and offline. It preserves `.gitmodules`, the AgentCanon gitlink, and the tracked symlink views. It needs no upstream token, checkout, updater, or network access.

## 3. Commit and validate

```bash
git diff --check
git add --all
git commit -m "Initialize my-project"
make pr-check
make fresh-clone-check
```

`make fresh-clone-check` requires a clean committed tree because it validates exactly what another user receives from an ordinary, non-recursive clone.

## 4. Activate the Codex runtime when needed

Before a Codex session that must load AgentCanon custom agents or hooks:

```bash
git submodule update --init --checkout -- vendor/agent-canon
git -C vendor/agent-canon rev-parse HEAD
git ls-files -s vendor/agent-canon
```

The checkout `HEAD` and staged gitlink must match. The root `AGENTS.md` and `.codex/{config.toml,agents,hooks.json,hooks}` symlinks then expose the AgentCanon-owned project runtime to Codex. Do not create a `tools/agent-canon` alias or copy AgentCanon tests, fixtures, or role files into the project tree.

## 5. Use Docker

```bash
docker build -t project-template -f docker/Dockerfile .
docker run --rm project-template python3 --version
```

For the repository checks:

```bash
make docker-check
make docker-build-check
make docker-run ARGS='cmake --version'
```
