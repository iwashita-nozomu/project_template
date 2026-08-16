# Docker environment boundary

## Decision

`docker/Dockerfile` is the single construction boundary for execution,
development, and validation. A running container may select a target, mount
source, wire identity, and execute commands. It may not create a virtual
environment, install packages, or materialize a second toolchain.

This separates two state classes:

```text
image state     = fixed runtimes + fixed tools + fixed dependency locks
workspace state = tracked source + generated build/test outputs
```

The image state is constructed once. Source is imported through
`PYTHONPATH=/workspace/project/python:/workspace/project`; the project is not
editable-installed. Consequently a bind mount cannot shadow an installed copy
of the package, and source edits are visible without mutating the image-owned
environment.

## Stage graph

- `node-provider` supplies Node.js/npm from a digest-pinned official image.
- `cpu-runtime` owns the digest-pinned Ubuntu base, Python 3.11.15 source build,
  native build tools, exact standard CLI versions, and the `project` identity.
- `gpu-runtime` adds pinned CUDA, cuDNN, and NCCL packages.
- `python-dependencies` creates root-owned `/opt/project-venv` from the tracked
  hash-locked requirements.
- `cpu-dev` combines `cpu-runtime` and the immutable Python environment.
- `gpu-dev` combines `gpu-runtime`, the CPU dependency environment, and the
  GPU lock.
- `cpu-validation` copies the repository, creates a synthetic Git commit, and
  runs the full local acceptance set during image build.
- `default-runtime` aliases `cpu-dev` for compatibility.

The static configuration snapshot remains repository data. The image does not
resolve, clone, synchronize, or execute a separate governance source tree.

## Reproducibility evidence

Base images are selected by digest. Python source and the CUDA repository
keyring are verified by SHA-256. Python packages are installed with
`--require-hashes`; npm tools use exact versions matching the Agent-Canon
standard dependency manifest. Image build reads back Python, Node.js, npm,
Codex, Pyright, and Bash language-server versions and records them together
with both requirements-file digests in
`/usr/local/share/project-template/image-manifest.txt`.

`/opt/project-venv` is root-owned while the runtime user is non-root. A mounted
repository therefore cannot rewrite the dependency environment. CI supplies
runner UID/GID as build arguments and verifies the resulting identity; the Dev
Container only supplies build arguments, target selection, fixed mount path,
and editor settings.

## Enforcement

`tools/check_environment_contract.py` rejects:

- a Dev Container Feature or lifecycle installation hook;
- the removed runtime installer and post-create script;
- package installation or venv creation in workflow/orchestration surfaces;
- a workflow that does not build and run `docker/Dockerfile` target `cpu-dev`;
- missing image stages, locks, exact standard CLI versions, or image-owned
  interpreter selection.

`docker/cold-build-smoke.sh --pull --no-cache` is the cold acceptance route. It
builds `cpu-validation` without cache and runs the resulting source-bearing
image without a bind mount.

References:

- [Ubuntu image](https://hub.docker.com/_/ubuntu)
- [Node.js image](https://hub.docker.com/_/node)
- [Python source releases](https://www.python.org/downloads/source/)
- [NVIDIA CUDA installation guide](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/#ubuntu)
- [JAX installation](https://docs.jax.dev/en/latest/installation.html)
