# Docker environment boundary

The tracked Dockerfile owns the base operating-system packages, pinned Python runtime, native toolchain, non-root identity, and optional GPU stage. The current project dependency installer consumes tracked lock files for CI and mounted-workspace smoke; moving those dependencies into an image-only development stage is tracked separately.

The Dev Container selects `docker/Dockerfile` directly. Its post-create command performs identity and mount validation only. It does not generate Compose, discover another source root, install packages, or execute an updater.

GitHub Actions checks the same Dockerfile with `docker/check_zero_build_contract.sh` and one cold build/smoke. Product source is mounted explicitly; no governance checkout, secret, or runtime module is part of the image contract.

References:

- [Ubuntu image](https://hub.docker.com/_/ubuntu)
- [Python source releases](https://www.python.org/downloads/source/)
- [NVIDIA CUDA installation guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/#ubuntu)
- [JAX installation](https://docs.jax.dev/en/latest/installation.html)
