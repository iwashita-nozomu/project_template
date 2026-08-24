# Docker environment

`docker/Dockerfile` defines one bounded Ubuntu 24.04 repository test image.
It contains only the dependencies required by the parent-owned portable Python
and C++ checks.

```bash
bash docker/run-tests.sh --tag project-template:test
```

The image contains the reviewed project source and runs as the non-root
`project` user. `test/testlist.toml` is the commented, parent-owned test
contract. `docker/run-tests.sh` runs `static` entries on the Host and
`portable` entries in the image. The runner emits the command, environment
owner, and responsibility when a test fails.

`docker/run-tests.sh` refuses to overwrite an existing image tag and removes
the exact image it creates. `docker/check_zero_build_contract.sh` validates the static boundary.
`docker/cold-build-smoke.sh --pull --no-cache` performs one cold build and
executes the same self-contained test runner. Neither path needs a workspace
mount or a development-container lifecycle.

Descendant repositories add product dependencies to their own project metadata
and Dockerfile. This template does not preinstall scientific Python, notebook,
CUDA, GPU, or general developer-tool profiles.
