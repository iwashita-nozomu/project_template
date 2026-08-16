# Quick start

## 1. Clone normally

```bash
git clone <template-url> my-project
cd my-project
```

Do not use recursive clone or submodule commands; the tracked tree is complete.

## 2. Preview and initialize

```bash
bash scripts/start_repository.sh \
  --project-slug my-project \
  --display-name "My Project" \
  --dry-run

bash scripts/start_repository.sh \
  --project-slug my-project \
  --display-name "My Project"
```

Initialization is local and offline. It needs no upstream token, checkout,
updater, or network access.

## 3. Commit the initialized tree

```bash
git diff --check
git add --all
git commit -m "Initialize my-project"
```

## 4. Enter the canonical environment

Open the repository as a Dev Container. On Linux, export the identity used by
the image build before opening VS Code:

```bash
export PROJECT_UID="$(id -u)"
export PROJECT_GID="$(id -g)"
code .
```

The Dev Container selects target `cpu-dev`, mounts the repository at
`/workspace/project`, and uses `/opt/project-venv/bin/python`. It has no
post-create installer.

A command-line equivalent is:

```bash
docker build --platform linux/amd64 \
  --build-arg "PROJECT_UID=$(id -u)" \
  --build-arg "PROJECT_GID=$(id -g)" \
  --target cpu-dev \
  --tag my-project:dev \
  --file docker/Dockerfile .

docker run --rm --platform linux/amd64 \
  --mount "type=bind,src=$PWD,dst=/workspace/project" \
  --workdir /workspace/project \
  --env PROJECT_TEMPLATE_IMAGE=1 \
  my-project:dev make pr-check
```

## 5. Validate the descendant lifecycle

Inside the canonical environment:

```bash
make pr-check
make fresh-clone-check
```

`make fresh-clone-check` requires a clean committed tree because it validates
exactly what another user receives from a normal clone. It reuses the image
capabilities and does not install dependencies in the generated repository.

The static files under `.codex/` are already present. Derived repositories do
not download or synchronize them.
