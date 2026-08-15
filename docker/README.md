# Docker environment

`docker/Dockerfile` defines the project image. The default target is CPU-only; `gpu-runtime` is explicit and relies on a compatible host driver.

```bash
docker build -t project-template -f docker/Dockerfile .
docker run --rm project-template python3 --version
```

`docker/check_zero_build_contract.sh` validates the static boundary. `docker/cold-build-smoke.sh --pull --no-cache` performs the cold build and a mounted-project smoke. Neither path installs or executes a separate governance runtime.
