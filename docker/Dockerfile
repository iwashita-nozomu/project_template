# syntax=docker/dockerfile:1.7

# Node is a fixed image capability. This provider and its digest mirror the
# Agent-Canon development-image contract; the final image remains Ubuntu based.
FROM --platform=linux/amd64 node:22.14.0-bullseye-slim@sha256:73a9dfbb6c761aebdf4666cce2627635a30d1d4c20f67ff642d01b8f09e709a3 AS node-provider

FROM --platform=linux/amd64 ubuntu:22.04@sha256:0d779ea97881505f5ef0039336ee85edba27519bdba968c284c86ee066a973c8 AS cpu-runtime

ARG PROJECT_USER=project
ARG PROJECT_UID=1000
ARG PROJECT_GID=1000
ARG PYTHON_VERSION=3.11.15
ARG PYTHON_SHA256=272179ddd9a2e41a0fc8e42e33dfbdca0b3711aa5abf372d3f2d51543d09b625

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CMAKE_GENERATOR=Ninja \
    PROJECT_TEMPLATE_CPP_BUILD_ROOT=/workspace/project/build/cpp \
    PROJECT_TEMPLATE_CPP_INSTALL_ROOT=/workspace/project/.state/cpp-install \
    PYTHONPATH=/workspace/project/python:/workspace/project \
    SHELL=/bin/zsh \
    HOME=/home/project \
    USER=project \
    NPM_CONFIG_UPDATE_NOTIFIER=false \
    NPM_CONFIG_FUND=false \
    NPM_CONFIG_AUDIT=false

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    xz-utils \
    gnupg \
    git \
    build-essential \
    pkg-config \
    cmake \
    ninja-build \
    psmisc \
    openssh-client \
    graphviz \
    jq \
    tree \
    rsync \
    zsh \
    sudo \
    python3-packaging \
    libbz2-dev \
    libdb-dev \
    libexpat1-dev \
    libffi-dev \
    libgdbm-dev \
    liblzma-dev \
    libncursesw5-dev \
    libnss3-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    tk-dev \
    uuid-dev \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    build_dir="$(mktemp -d)"; \
    archive="${build_dir}/Python-${PYTHON_VERSION}.tar.xz"; \
    curl --fail --location --silent --show-error \
      "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz" \
      --output "$archive"; \
    printf '%s  %s\n' "$PYTHON_SHA256" "$archive" | sha256sum --check --strict; \
    tar --extract --xz --file "$archive" --directory "$build_dir" \
      --no-same-owner --no-same-permissions; \
    cd "$build_dir/Python-${PYTHON_VERSION}"; \
    ./configure --prefix=/usr/local --with-ensurepip=install; \
    make -j"$(nproc)"; \
    make altinstall; \
    ln -sfn /usr/local/bin/python3.11 /usr/local/bin/python3; \
    ln -sfn /usr/local/bin/pip3.11 /usr/local/bin/pip3; \
    install -d -m 0755 /usr/local/lib/python3.11/site-packages; \
    printf '%s\n' /usr/lib/python3/dist-packages \
      > /usr/local/lib/python3.11/site-packages/ubuntu-dist-packages.pth; \
    python3 --version | grep -F "$PYTHON_VERSION"; \
    python3 -m pip --version; \
    rm -rf "$build_dir"

# Copy the digest-pinned official Node payload instead of adding a second apt
# repository. Exact standard CLI versions follow Agent-Canon's declared tools.
COPY --from=node-provider /usr/local/bin/node /usr/local/bin/node
COPY --from=node-provider /usr/local/lib/node_modules /usr/local/lib/node_modules
COPY --from=node-provider /usr/local/bin/npm /usr/local/bin/npm
COPY --from=node-provider /usr/local/bin/npx /usr/local/bin/npx
COPY --from=node-provider /usr/local/bin/corepack /usr/local/bin/corepack
RUN set -eux; \
    ln -sfn ../lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm; \
    ln -sfn ../lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx; \
    ln -sfn ../lib/node_modules/corepack/dist/corepack.js /usr/local/bin/corepack; \
    npm install --global \
      @openai/codex@0.145.0 \
      pyright@1.1.411 \
      bash-language-server@5.6.0; \
    codex --version | grep -F '0.145.0'; \
    pyright --version | grep -F '1.1.411'; \
    bash-language-server --version | grep -F '5.6.0'; \
    npm cache clean --force

COPY docker/register_safe_directories.sh /usr/local/bin/project-template-register-safe-directories
RUN chmod 0755 /usr/local/bin/project-template-register-safe-directories

RUN set -eux; \
    case "$PROJECT_USER" in project) ;; *) echo "PROJECT_USER must be project" >&2; exit 1 ;; esac; \
    case "$PROJECT_UID" in ''|0|0*|*[!0-9]*) echo "PROJECT_UID must be a nonzero decimal" >&2; exit 1 ;; esac; \
    case "$PROJECT_GID" in ''|0|0*|*[!0-9]*) echo "PROJECT_GID must be a nonzero decimal" >&2; exit 1 ;; esac; \
    [ "$PROJECT_UID" -ge 1000 ] || { echo "PROJECT_UID must not overlap system users" >&2; exit 1; }; \
    getent passwd "$PROJECT_USER" >/dev/null 2>&1 && { echo "project user-name collision" >&2; exit 1; } || true; \
    getent passwd "$PROJECT_UID" >/dev/null 2>&1 && { echo "PROJECT_UID collision" >&2; exit 1; } || true; \
    if getent group "$PROJECT_GID" >/dev/null 2>&1; then \
      primary_group="$PROJECT_GID"; \
    else \
      getent group "$PROJECT_USER" >/dev/null 2>&1 && { echo "project group-name collision" >&2; exit 1; } || true; \
      groupadd --gid "$PROJECT_GID" "$PROJECT_USER"; \
      primary_group="$PROJECT_USER"; \
    fi; \
    useradd --uid "$PROJECT_UID" --gid "$primary_group" --create-home --shell /bin/zsh "$PROJECT_USER"; \
    install -d -m 0755 -o "$PROJECT_UID" -g "$PROJECT_GID" \
      /workspace /workspace/project "/home/$PROJECT_USER/.config" "/home/$PROJECT_USER/.local"; \
    printf '%s\n' '# Image-owned default shell configuration.' > "/home/$PROJECT_USER/.zshrc"; \
    printf '%s ALL=(ALL) NOPASSWD:ALL\n' "$PROJECT_USER" > "/etc/sudoers.d/$PROJECT_USER"; \
    chmod 0440 "/etc/sudoers.d/$PROJECT_USER"; \
    visudo --check --file="/etc/sudoers.d/$PROJECT_USER"; \
    chown "$PROJECT_UID:$PROJECT_GID" "/home/$PROJECT_USER/.zshrc"; \
    test "$(id -u "$PROJECT_USER")" = "$PROJECT_UID"; \
    test "$(id -g "$PROJECT_USER")" = "$PROJECT_GID"

WORKDIR /workspace/project
EXPOSE 8888
CMD ["/bin/zsh"]
USER project

FROM cpu-runtime AS gpu-runtime

ARG CUDA_KEYRING_URL=https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
ARG CUDA_KEYRING_SHA256=d93190d50b98ad4699ff40f4f7af50f16a76dac3bb8da1eaaf366d47898ff8df
ENV PATH=/usr/local/cuda/bin:/usr/local/bin:${PATH} \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64
USER root
RUN set -eux; \
    keyring_deb=/tmp/cuda-keyring.deb; \
    curl --fail --location --silent --show-error "$CUDA_KEYRING_URL" --output "$keyring_deb"; \
    printf '%s  %s\n' "$CUDA_KEYRING_SHA256" "$keyring_deb" | sha256sum --check --strict; \
    dpkg --install "$keyring_deb"; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      cuda-toolkit-12-8=12.8.2-1 \
      libcudnn9-cuda-12=9.8.0.87-1 \
      libcudnn9-dev-cuda-12=9.8.0.87-1 \
      libnccl2=2.25.1-1+cuda12.8 \
      libnccl-dev=2.25.1-1+cuda12.8; \
    rm -f "$keyring_deb"; \
    rm -rf /var/lib/apt/lists/*
USER project

FROM cpu-runtime AS python-dependencies
USER root
COPY docker/requirements.txt /opt/project-locks/requirements.txt
COPY docker/requirements-gpu.txt /opt/project-locks/requirements-gpu.txt
RUN set -eux; \
    python3 -m venv /opt/project-venv; \
    /opt/project-venv/bin/python -m pip install --require-hashes \
      --no-cache-dir --disable-pip-version-check \
      -r /opt/project-locks/requirements.txt; \
    /opt/project-venv/bin/python -m pip check; \
    find /opt/project-venv -xdev -type d -exec chmod 0755 {} +; \
    find /opt/project-venv -xdev -type f -exec chmod go-w {} +

FROM cpu-runtime AS cpu-dev
ENV VIRTUAL_ENV=/opt/project-venv \
    PATH=/usr/local/bin:/opt/project-venv/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin \
    PROJECT_TEMPLATE_IMAGE=1
USER root
COPY --from=python-dependencies /opt/project-venv /opt/project-venv
COPY --from=python-dependencies /opt/project-locks /opt/project-locks
RUN set -eux; \
    install -d -m 0755 /usr/local/share/project-template; \
    { \
      printf 'schema=project-template-image-manifest-v1\n'; \
      sha256sum /opt/project-locks/requirements.txt /opt/project-locks/requirements-gpu.txt; \
      python3 --version; \
      node --version; \
      npm --version; \
      codex --version; \
      pyright --version; \
      bash-language-server --version; \
    } > /usr/local/share/project-template/image-manifest.txt; \
    chmod 0444 /usr/local/share/project-template/image-manifest.txt; \
    test "$(stat -c %u /opt/project-venv)" = 0; \
    /opt/project-venv/bin/python -m pip check
USER project

FROM gpu-runtime AS gpu-dev
ENV VIRTUAL_ENV=/opt/project-venv \
    PATH=/usr/local/cuda/bin:/usr/local/bin:/opt/project-venv/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/sbin:/bin \
    PROJECT_TEMPLATE_IMAGE=1
USER root
COPY --from=python-dependencies /opt/project-venv /opt/project-venv
COPY --from=python-dependencies /opt/project-locks /opt/project-locks
RUN set -eux; \
    /opt/project-venv/bin/python -m pip install --require-hashes \
      --no-cache-dir --disable-pip-version-check \
      -r /opt/project-locks/requirements-gpu.txt; \
    /opt/project-venv/bin/python -m pip check; \
    find /opt/project-venv -xdev -type f -exec chmod go-w {} +
USER project

FROM cpu-dev AS cpu-validation
ARG PROJECT_UID=1000
ARG PROJECT_GID=1000
ENV VALIDATION_IMAGE=1
USER root
COPY --chown=${PROJECT_UID}:${PROJECT_GID} . /workspace/project
USER project
RUN set -eux; \
    git init --initial-branch=main; \
    git config user.email validation@localhost; \
    git config user.name 'Validation Image'; \
    git add --all; \
    git commit -m 'Materialize validation source'; \
    make full-check-local; \
    make image-smoke-local

FROM cpu-dev AS default-runtime
USER project
