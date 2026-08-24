# Docker environment boundary

The tracked Dockerfile owns one Ubuntu 24.04 test image: the distro Python
runtime, an image-local Python virtual environment, the native C++ test
toolchain, non-root identity, and the reviewed project source. It installs only
the dependencies required by the repository's portable tests. Scientific
Python, notebook, CUDA, GPU, and general developer-tool profiles are descendant
project responsibilities rather than template defaults.

The project uses `docker/Dockerfile` directly. `test/testlist.toml` is the
commented command contract and `test/testrunner.sh` is its single execution
entrypoint. Static entries execute on the Host before build; portable tooling
and C++ entries execute in the image. Each failed command reports its command,
`environment_owner`, and `responsibility`.

GitHub Actions checks the same Dockerfile with
`docker/check_zero_build_contract.sh` and one build/test run through
`docker/run-tests.sh`. The image
does not require an external source mount or a development-container
lifecycle.

The run script owns the temporary image tag and removes it on every exit path.
The cold-build wrapper reuses that lifecycle with `--pull --no-cache`.

Reference: [Ubuntu image](https://hub.docker.com/_/ubuntu)
