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
Keep the Python lock under [dependencies/](dependencies/README.md). Declare C++
library dependencies in the root `CMakeLists.txt`, using commit-pinned
`FetchContent` declarations. Each C++ experiment or validation case has its own
CMake project and consumes the library target; it declares only its additional
dependencies. See the [C++ build layout](documents/design/cpp-build-layout.md)
and the standalone [version validation commands](test/cpp/README.md).

## 3. Optionally use the Docker dependency example

```bash
docker build -f docker/Dockerfile -t project-template:dependencies .
docker run --rm project-template:dependencies python --version
```

The image is a dependency and runtime example. A derived project may replace
the lock, OS packages, entrypoint, and validation commands for its own needs.

## 4. Run a file with Make and Docker

```bash
make test/cpp/version/version_test.cpp
# The basename also works when unique:
make version_test.cpp
```

For Python, use `make path/to/script.py`; pass program arguments with
`ARGS='"two words" --option'`. The file must exist in your working tree.
The [file runner](docker/README.md#run-a-source-file) builds the Docker image
using its cache and runs the current source, with build outputs under `workspace/`.
