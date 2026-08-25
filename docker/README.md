# Docker environment

`docker/Dockerfile` is a single Ubuntu 24.04 dependency-installation example.
It demonstrates OS packages, an image-local Python virtual environment, a
hash-pinned dependency lock, and a non-root runtime user.

```bash
docker build -f docker/Dockerfile -t project-template:dependencies .
docker run --rm project-template:dependencies python --version
```

The image contains the reviewed project source and runs as the non-root
`project` user. Derived projects may replace the dependency lock, add build
tools, and choose their own entrypoint and validation commands.

Descendant repositories add product dependencies to their own project metadata
and Dockerfile. This template does not preinstall scientific Python, notebook,
CUDA, GPU, or general developer-tool profiles.
