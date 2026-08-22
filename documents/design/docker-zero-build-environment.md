# Docker environment boundary

The tracked Dockerfile owns the base operating-system packages, pinned Python
runtime, native toolchain, non-root identity, optional GPU stage, and the
reviewed project source. The project test dependency is installed in the
image, so the same artifact can run the parent test list without host Python
state.

The project uses `docker/Dockerfile` directly. `test/testlist.toml` is the
commented command contract and `test/testrunner.sh` is its single execution
entrypoint. Each failed command reports its command, `environment_owner`, and
`responsibility`, keeping product failures attributable to the project
container.

GitHub Actions checks the same Dockerfile with
`docker/check_zero_build_contract.sh` and one cold build/test run. The image
does not require an external source mount or a development-container
lifecycle.

References:

- [Ubuntu image](https://hub.docker.com/_/ubuntu)
- [Python source releases](https://www.python.org/downloads/source/)
- [NVIDIA CUDA installation guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/#ubuntu)
- [JAX installation](https://docs.jax.dev/en/latest/installation.html)
