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

The Dockerfile demonstrates where a derived project places OS packages, Python
dependencies, the virtual environment, and the non-root runtime user. It is an
example input, not a required host environment.

The image is a bounded Ubuntu 24.04 dependency example. It intentionally omits
scientific Python, notebook, CUDA, GPU, and general developer-tool profiles;
descendant repositories add only the product dependencies they actually need.

## Repository layout

```text
.
├── AGENTS.md                  # project instructions
├── CMakeLists.txt            # root C++ project entrypoint
├── include/                  # public C++ headers
├── src/                      # production C++ sources
├── python/                   # Python package source
├── experiments/              # project experiments
├── documents/                # project contracts, design, notes, and sources
├── docker/                   # dependency-installation image example
├── test/                     # optional project test sources
├── vendor/                   # empty placeholder for project-owned third-party sources
└── workspace/                # ignored project scratch space
```

See `QUICK_START.md`, `docker/README.md`, and
`documents/design/docker-zero-build-environment.md` for the dependency example.
