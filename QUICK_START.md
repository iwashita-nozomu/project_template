# Quick start

## 1. Clone normally

```bash
git clone <template-url> my-project
cd my-project
```

A normal clone contains only project-owned source and examples. It does not
require a bootstrap script, validation runner, CI setup, or external tool
checkout.

## 2. Inspect the project layout

```bash
find src include python test documents docker -maxdepth 2 -type f | sort
git status --short
```

Derived projects choose their own identity conversion and validation workflow.

## 3. Use the Docker dependency example

```bash
docker build -f docker/Dockerfile -t project-template:dependencies .
docker run --rm project-template:dependencies python --version
```

The image is a dependency and runtime example. A derived project may replace
the lock, OS packages, entrypoint, and validation commands for its own needs.
