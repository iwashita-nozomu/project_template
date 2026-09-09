# Docker dependency example

The tracked Dockerfile is an Ubuntu 24.04 dependency example: it shows a
distro Python runtime, an image-local Python virtual environment, native build
tools, a non-root identity, and a reviewed source snapshot. It is not a
required project validation environment.

Language dependency installation definitions live in
[dependencies/](../../dependencies/README.md). The Dockerfile consumes
`dependencies/python/requirements.txt` before copying the source snapshot.
`dependencies/cpp/CMakeLists.txt` is an independent empty entrypoint that derived
projects can populate and invoke in a dependency layer when needed. OS package
installation remains in the Dockerfile.

Build and run the example directly:

```bash
docker build -f docker/Dockerfile -t project-template:dependencies .
docker run --rm project-template:dependencies python --version
```

Derived projects own their build, test, CI, and cleanup commands.

Reference: [Ubuntu image](https://hub.docker.com/_/ubuntu)
