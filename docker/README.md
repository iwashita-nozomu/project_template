# Docker environment

`docker/Dockerfile` defines three explicit project surfaces:

- default `default-runtime`: bounded repository test image;
- `full-runtime`: project and development Python dependencies;
- `gpu-runtime`: full GPU Python dependencies plus the pinned CUDA stack.

```bash
bash docker/run-tests.sh --tag project-template:test

docker build --target full-runtime -f docker/Dockerfile -t project-template:full .
docker build --target gpu-runtime -f docker/Dockerfile -t project-template:gpu .
```

The image contains the reviewed project source and runs as the non-root
`project` user. `test/testlist.toml` is the commented, parent-owned test
contract; `test/testrunner.sh` executes each command from that list and emits
the command, environment owner, and responsibility when a test fails.

`docker/run-tests.sh` refuses to overwrite an existing image tag and removes
the exact image it creates. `docker/check_zero_build_contract.sh` validates the static boundary.
`docker/cold-build-smoke.sh --pull --no-cache` performs one cold build and
executes the same self-contained test runner. Neither path needs a workspace
mount or a development-container lifecycle.
