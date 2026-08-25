# Docker dependency example

The tracked Dockerfile is an Ubuntu 24.04 dependency example: it shows a
distro Python runtime, an image-local Python virtual environment, native build
tools, a non-root identity, and a reviewed source snapshot. It is not a
required project validation environment.

Build and run the example directly:

```bash
docker build -f docker/Dockerfile -t project-template:dependencies .
docker run --rm project-template:dependencies python --version
```

Derived projects own their build, test, CI, and cleanup commands.

Reference: [Ubuntu image](https://hub.docker.com/_/ubuntu)
