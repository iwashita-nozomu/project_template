# Docker dependency example

The tracked Dockerfile is an Ubuntu 24.04 dependency example: it shows a
distro Python runtime, an image-local Python virtual environment, native build
tools, a non-root identity, and a reviewed source snapshot. It is not a
required project validation environment.

The Dockerfile consumes the Python lock at
`dependencies/python/requirements.txt` before copying the source snapshot.
OS package installation remains in the Dockerfile. C++ library dependencies
are declared and resolved by the root CMake project, as described in the
[C++ build layout](cpp-build-layout.md).

Build and run the example directly:

```bash
docker build -f docker/Dockerfile -t project-template:dependencies .
docker run --rm project-template:dependencies python --version
```

Derived projects own their build, test, CI, and cleanup commands.

Reference: [Ubuntu image](https://hub.docker.com/_/ubuntu)
