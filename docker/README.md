# Docker environment

`docker/Dockerfile` owns the complete project environment. `cpu-dev` is the
standard development/validation target; `gpu-dev` adds the pinned CUDA stack.
No post-create or CI step installs dependencies.

Build the CPU image with the host identity:

```bash
docker build --platform linux/amd64 \
  --build-arg "PROJECT_UID=$(id -u)" \
  --build-arg "PROJECT_GID=$(id -g)" \
  --target cpu-dev \
  --tag project-template:dev \
  --file docker/Dockerfile .
```

Run the mounted repository checks:

```bash
docker run --rm --platform linux/amd64 \
  --mount "type=bind,src=$PWD,dst=/workspace/project" \
  --workdir /workspace/project \
  --env PROJECT_TEMPLATE_IMAGE=1 \
  project-template:dev \
  make pr-check
```

Build-time full acceptance copies the source into an image and needs no mount:

```bash
docker build --platform linux/amd64 \
  --build-arg "PROJECT_UID=$(id -u)" \
  --build-arg "PROJECT_GID=$(id -g)" \
  --target cpu-validation \
  --tag project-template:validation \
  --file docker/Dockerfile .
```

The cold contract is:

```bash
bash docker/cold-build-smoke.sh --pull --no-cache
```

`docker/check_zero_build_contract.sh` statically validates image ownership and
projection boundaries. `/opt/project-venv` is root-owned, source is loaded from
the mounted workspace, and exact tool/lock evidence is stored in
`/usr/local/share/project-template/image-manifest.txt`.
