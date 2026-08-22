# Docker environment

`docker/Dockerfile` defines the project image. The default target is CPU-only; `gpu-runtime` is explicit and relies on a compatible host driver.

```bash
docker build -f docker/Dockerfile -t project-template .
docker run --rm project-template test/testrunner.sh
```

The image contains the reviewed project source and runs as the non-root
`project` user. `test/testlist.toml` is the commented, parent-owned test
contract; `test/testrunner.sh` executes each command from that list and emits
the command, environment owner, and responsibility when a test fails.

`docker/check_zero_build_contract.sh` validates the static boundary.
`docker/cold-build-smoke.sh --pull --no-cache` performs one cold build and
executes the same self-contained test runner. Neither path needs a workspace
mount or a development-container lifecycle.
