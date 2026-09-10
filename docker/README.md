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

Keep Python dependency definitions under [dependencies/](../dependencies/README.md)
and OS packages in the Dockerfile. The Python lock is copied before the source
snapshot to preserve dependency layer caching. C++ library dependencies belong
in the root CMake project and are resolved when that project is configured;
experiments and validation cases consume its targets. See the
[C++ build layout](../documents/design/cpp-build-layout.md).

This template does not preinstall scientific Python, notebook, CUDA, GPU, or
general developer-tool profiles.
