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

The template has no project bootstrap or validation command. Derived projects
choose their own identity, build, and validation workflow.

## Docker dependency example

```bash
docker build -f docker/Dockerfile -t project-template:dependencies .
docker run --rm project-template:dependencies python --version
```

The Dockerfile demonstrates OS packages, the virtual environment, and the
non-root runtime user. Language dependency definitions live in
[dependencies/](dependencies/README.md), and the image installs the Python lock.
The Dockerfile is an example input, not a required host environment.

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
├── dependencies/                 # external dependency installation definitions
│   ├── README.md                 # dependency addition and usage guide
│   ├── cpp/CMakeLists.txt        # empty C++ dependency entrypoint
│   └── python/requirements.txt   # Python dependency lock example
├── docker/                       # container definition and usage example
├── test/                         # optional project test sources
├── vendor/                       # empty placeholder for project-owned third-party sources
└── workspace/                    # ignored project scratch space
```

CMake configuration lives with each purpose: the product root, dependency
installation, and individual C++ experiments and tests. Local `CMakeLists.txt`
files may define independent projects or be included with `add_subdirectory()`;
see the [C++ build layout](documents/design/cpp-build-layout.md).

See [QUICK_START.md](QUICK_START.md), [dependencies/README.md](dependencies/README.md),
and [docker/README.md](docker/README.md) for setup and dependency examples.
