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
find src include python test documents dependencies docker -maxdepth 2 -type f | sort
git status --short
```

Derived projects choose their own identity conversion and validation workflow.
Add language dependencies under [dependencies/](dependencies/README.md):
`cpp/CMakeLists.txt` is an empty C++ dependency entrypoint, and
`python/requirements.txt` is the Python lock example. The product C++ build
starts at the root `CMakeLists.txt`. Individual C++ experiments and tests keep
their own local CMake configuration and may define independent projects; see
the [C++ build layout](documents/design/cpp-build-layout.md).

## 3. Optionally use the Docker dependency example

```bash
docker build -f docker/Dockerfile -t project-template:dependencies .
docker run --rm project-template:dependencies python --version
```

The image is a dependency and runtime example. A derived project may replace
the lock, OS packages, entrypoint, and validation commands for its own needs.
