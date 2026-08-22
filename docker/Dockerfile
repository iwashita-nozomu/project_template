FROM ubuntu:22.04@sha256:0d779ea97881505f5ef0039336ee85edba27519bdba968c284c86ee066a973c8 AS cpu-runtime

ARG PROJECT_UID=1000
ARG PROJECT_GID=1000
ARG PYTHON_VERSION=3.11.15
ARG PYTHON_SHA256=272179ddd9a2e41a0fc8e42e33dfbdca0b3711aa5abf372d3f2d51543d09b625

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CMAKE_GENERATOR=Ninja \
    PROJECT_TEMPLATE_CPP_BUILD_ROOT=/workspace/build/cpp \
    PROJECT_TEMPLATE_CPP_INSTALL_ROOT=/workspace/.state/cpp-install \
    PROJECT_TEST_ENVIRONMENT_OWNER=project-container \
    PYTHONPATH=/workspace/project-template/python \
    SHELL=/bin/zsh \
    HOME=/home/project

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
    rsync \
    zsh \
    python3-packaging \
    python3-venv \
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
    printf '%s  %s\n' "$PYTHON_SHA256" "$archive" | sha256sum --check -; \
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
    python3 --version; \
    python3 -m pip --version; \
    python3 -c 'from packaging.requirements import Requirement; Requirement("pyyaml>=6")'; \
    rm -rf "$build_dir"

COPY docker/requirements-test.txt /tmp/project-test-requirements.txt
RUN python3 -m pip install --no-cache-dir --require-hashes \
      --requirement /tmp/project-test-requirements.txt \
 && rm -f /tmp/project-test-requirements.txt

RUN set -eux; \
    case "$PROJECT_UID" in ''|0|*[!0-9]*) echo "PROJECT_UID must be positive" >&2; exit 1 ;; esac; \
    case "$PROJECT_GID" in ''|0|*[!0-9]*) echo "PROJECT_GID must be positive" >&2; exit 1 ;; esac; \
    groupadd --gid "$PROJECT_GID" project; \
    useradd --uid "$PROJECT_UID" --gid "$PROJECT_GID" --create-home --shell /bin/zsh project; \
    install -d -m 0755 -o project -g project /workspace; \
    install -d -m 0755 -o project -g project /home/project/.config /home/project/.local; \
    printf '%s\n' '# Image-owned default shell configuration.' > /home/project/.zshrc; \
    chown project:project /home/project/.zshrc; \
    test "$(id -u project)" = "$PROJECT_UID"; \
    test "$(id -u project)" != 0; \
    test "$(id -g project)" = "$PROJECT_GID"

# The product image is self-contained: tests run against the exact source that
# was reviewed at build time, with no external lifecycle hook.
COPY --chown=project:project . /workspace/project-template
WORKDIR /workspace/project-template
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
    printf '%s  %s\n' "$CUDA_KEYRING_SHA256" "$keyring_deb" | sha256sum --check -; \
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

FROM cpu-runtime AS default-runtime
USER project
