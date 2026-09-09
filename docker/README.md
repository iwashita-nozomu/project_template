# Docker environment

`docker/Dockerfile` is a single Ubuntu 24.04 dependency-installation example.
It demonstrates OS packages, an image-local Python virtual environment, a
hash-pinned [Python dependency lock](../dependencies/python/requirements.txt),
and a non-root runtime user.

```bash
docker build -f docker/Dockerfile -t project-template:dependencies .
docker run --rm project-template:dependencies python --version
```

The image contains the reviewed project source and runs as the non-root
`project` user. Derived projects may replace the dependency lock, add build
tools, and choose their own entrypoint and validation commands.

Add language dependency definitions under [dependencies/](../dependencies/README.md)
and OS packages in the Dockerfile. The Python lock is copied before the source
snapshot to preserve dependency layer caching. When C++ libraries are needed,
add them to `dependencies/cpp/CMakeLists.txt` and invoke that entrypoint in a
dependency layer before copying the source snapshot. The empty C++ entrypoint
requires no Docker build step.

This template does not preinstall scientific Python, notebook, CUDA, GPU, or
general developer-tool profiles.
