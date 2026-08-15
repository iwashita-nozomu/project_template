# Quick start

## 1. Clone normally

```bash
git clone <template-url> my-project
cd my-project
```

Do not use recursive clone or submodule commands; the tracked tree is complete.

## 2. Preview and initialize

```bash
bash scripts/start_repository.sh \
  --project-slug my-project \
  --display-name "My Project" \
  --dry-run

bash scripts/start_repository.sh \
  --project-slug my-project \
  --display-name "My Project"
```

Initialization is local and offline. It needs no upstream token, checkout, updater, or network access.

## 3. Commit and validate

```bash
git diff --check
git add --all
git commit -m "Initialize my-project"
make pr-check
make fresh-clone-check
```

`make fresh-clone-check` requires a clean committed tree because it validates exactly what another user receives from a normal clone.

## 4. Use Docker

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

The static files under `.codex/` are already present. Derived repositories do not download or synchronize them.
