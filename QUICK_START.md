# Quick start

## 1. Clone normally

```bash
git clone <template-url> my-project
cd my-project
```

A normal clone contains only project-owned source. Project bootstrap, build,
tests, documentation, Docker, and CI do not require an external tool checkout
or hidden runtime state.

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
bash test/testrunner.sh
bash tools/check_fresh_clone.sh
```

`tools/check_fresh_clone.sh` requires a clean committed tree because it validates exactly what another user receives from an ordinary, non-recursive clone.

## 4. Use Docker

```bash
bash docker/run-tests.sh --tag project-template:test
```

The Docker wrapper executes the same complete repository test list and removes
the exact temporary image.
