# Project Template

A starting point for Python, C++, documents, experiments, and containerized
project development. It owns product code, a Docker dependency example,
documents, and local project policy.

A normal clone contains the project source layout and dependency-template
documents. It does not require a bootstrap script, validation runner, CI setup,
or external tool checkout.

## Start a project

```bash
git clone <template-url> my-project
cd my-project
git status --short
```

The template has no required project bootstrap or validation command. Derived
projects choose their own identity, build, execution, and validation workflow.
The checked-in [GitHub CI example](.github/workflows/ci.yml) builds the library,
runs the standalone C++ validation case, and checks the optional source runner.
It requires no Docker or external tool checkout; descendants may replace it
with their own CI.

## Docker dependency example

```bash
docker build -f docker/Dockerfile -t project-template:dependencies .
docker run --rm project-template:dependencies python --version
```

The Dockerfile demonstrates OS packages, the virtual environment, and the
non-root runtime user. The image installs the Python lock from
[dependencies/](dependencies/README.md); C++ library dependencies are declared
in the root CMake project.
The Dockerfile is an example input, not a required host environment. A derived
project owns its container execution and host mount policy.

For a single source file, the optional [Make and Docker runner](docker/README.md#run-a-source-file)
can run Python or build and run a C++ executable:

```bash
make test/cpp/version/version_test.cpp
make path/to/script.py ARGS='"two words" --verbose'
```

The runner uses the example image and requires a working Docker daemon. Direct
Python and CMake commands remain available without this helper.

The image is a bounded Ubuntu 24.04 dependency example. It intentionally omits
scientific Python, notebook, CUDA, GPU, and general developer-tool profiles;
descendant repositories add only the product dependencies they actually need.

## Repository layout

```text
.
├── AGENTS.md                     # project instructions
├── CMakeLists.txt                # product C++ build entrypoint
├── include/                      # public C++ headers
├── src/                          # production C++ sources
├── python/                       # Python package source
├── experiments/                  # project experiments
├── documents/                    # project contracts, design, notes, and sources
├── dependencies/                 # Python dependency installation definitions
│   ├── README.md                 # dependency addition and usage guide
│   └── python/requirements.txt   # Python dependency lock example
├── docker/                       # container definition and usage example
├── test/                         # optional project test sources
├── vendor/                       # empty placeholder for project-owned third-party sources
└── workspace/                    # ignored project scratch space
```

The root CMake project builds only the library and its C++ dependencies; it
never reads test or experiment projects. Individual
C++ experiments and validation cases own their executables and additional
dependencies, consuming the library through `FetchContent` or `add_subdirectory()`.
See the [C++ build layout](documents/design/cpp-build-layout.md) and the runnable
[version validation case](test/cpp/README.md).

See [QUICK_START.md](QUICK_START.md), [dependencies/README.md](dependencies/README.md),
and [docker/README.md](docker/README.md) for setup and dependency examples.
