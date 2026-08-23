# Docker environment boundary

The tracked Dockerfile owns the base operating-system packages, pinned Python
runtime, native toolchain, non-root identity, explicit full/GPU stages, and the
reviewed project source. The default target installs only the repository test
dependency. `full-runtime` and `gpu-runtime` consume the reviewed project locks;
CI does not pay that dependency cost when it only validates the repository.

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

References:

- [Ubuntu image](https://hub.docker.com/_/ubuntu)
- [Python source releases](https://www.python.org/downloads/source/)
- [NVIDIA CUDA installation guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/#ubuntu)
- [JAX installation](https://docs.jax.dev/en/latest/installation.html)
