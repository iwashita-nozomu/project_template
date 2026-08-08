# @dependency-start
# contract environment
# responsibility Builds the reproducible Ubuntu 22.04 parent product image and its non-root runtime boundary.
# upstream design ../documents/design/docker-zero-build-environment.md direct base, stage order, and owner split
# upstream design ../vendor/agent-canon/CONTAINER_OPERATIONS.md product image versus mounted AgentCanon tools
# downstream implementation install_python_dependencies.sh installs the parent Python lock after workspace mount
# downstream environment ../.devcontainer/post-create-parent.sh validates the final parent runtime identity
# @dependency-end

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
    PROJECT_TEMPLATE_CPP_BUILD_ROOT=/workspace/build/cpp \
    PROJECT_TEMPLATE_CPP_INSTALL_ROOT=/workspace/.state/cpp-install \
    PYTHONPATH=/workspace/python \
    SHELL=/bin/zsh \
    HOME=/home/project

# Ubuntu fundamentals and deterministic build dependencies.  Node/npm, ninja-build,
# tree, and the remaining derived developer tools are intentionally owned by the
# fixed AgentCanon bootstrap or its merged dependency manifest.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    xz-utils \
    gnupg \
    git \
    docker.io \
    build-essential \
    pkg-config \
    cmake \
    psmisc \
    openssh-client \
    graphviz \
    rsync \
    zsh \
    sudo \
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

# Jammy's official archive does not provide the required Python 3.11 package.
# Build the selected CPython release from the Python.org source archive rather
# than using a PPA, moving installer, or host interpreter.
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

COPY docker/register_safe_directories.sh /usr/local/bin/project-template-register-safe-directories
RUN chmod 0755 /usr/local/bin/project-template-register-safe-directories

# The runtime identity is canonical: PROJECT_USER may be supplied only as the
# public name `project`; UID/GID are positive decimal values and are materialized
# by the devcontainer generator from the host workspace identity.
RUN set -eux; \
    case "$PROJECT_USER" in \
      project) ;; \
      *) echo "PROJECT_USER must be canonical project" >&2; exit 1 ;; \
    esac; \
    case "$PROJECT_UID" in \
      ''|0|*[!0-9]*) echo "PROJECT_UID must be a positive decimal integer" >&2; exit 1 ;; \
    esac; \
    case "$PROJECT_GID" in \
      ''|0|*[!0-9]*) echo "PROJECT_GID must be a positive decimal integer" >&2; exit 1 ;; \
    esac; \
    existing_project_user_uid="$(getent passwd "$PROJECT_USER" | cut -d: -f3 || true)"; \
    if [ -n "$existing_project_user_uid" ] && [ "$existing_project_user_uid" != "$PROJECT_UID" ]; then \
      echo "PROJECT_UID collides with the existing project user" >&2; exit 1; \
    fi; \
    existing_project_group_gid="$(getent group "$PROJECT_USER" | cut -d: -f3 || true)"; \
    if [ -n "$existing_project_group_gid" ] && [ "$existing_project_group_gid" != "$PROJECT_GID" ]; then \
      echo "PROJECT_GID collides with the existing project group" >&2; exit 1; \
    fi; \
    existing_uid_user="$(getent passwd "$PROJECT_UID" | cut -d: -f1 || true)"; \
    if [ -n "$existing_uid_user" ] && [ "$existing_uid_user" != "$PROJECT_USER" ]; then \
      [ "$PROJECT_UID" -ge 1000 ] || { echo "PROJECT_UID collides with a system identity" >&2; exit 1; }; \
      [ -z "$existing_project_user_uid" ] || { echo "PROJECT_UID has two incompatible users" >&2; exit 1; }; \
      usermod --login "$PROJECT_USER" "$existing_uid_user"; \
    fi; \
    existing_gid_group="$(getent group "$PROJECT_GID" | cut -d: -f1 || true)"; \
    if [ -n "$existing_gid_group" ] && [ "$existing_gid_group" != "$PROJECT_USER" ]; then \
      [ "$PROJECT_GID" -ge 1000 ] || { echo "PROJECT_GID collides with a system identity" >&2; exit 1; }; \
      [ -z "$existing_project_group_gid" ] || { echo "PROJECT_GID has two incompatible groups" >&2; exit 1; }; \
      groupmod --new-name "$PROJECT_USER" "$existing_gid_group"; \
    fi; \
    if ! getent group "$PROJECT_USER" >/dev/null 2>&1; then \
      groupadd --gid "$PROJECT_GID" "$PROJECT_USER"; \
    fi; \
    if ! getent passwd "$PROJECT_USER" >/dev/null 2>&1; then \
      useradd --uid "$PROJECT_UID" --gid "$PROJECT_USER" \
        --create-home --shell /bin/zsh "$PROJECT_USER"; \
    fi; \
    usermod --gid "$PROJECT_USER" --shell /bin/zsh "$PROJECT_USER"; \
    project_home="$(getent passwd "$PROJECT_USER" | cut -d: -f6)"; \
    if [ "$project_home" != "/home/$PROJECT_USER" ]; then \
      [ ! -e "/home/$PROJECT_USER" ] || { echo "project home path is occupied" >&2; exit 1; }; \
      usermod --home "/home/$PROJECT_USER" --move-home "$PROJECT_USER"; \
    fi; \
    install -d -m 0755 -o "$PROJECT_USER" -g "$PROJECT_USER" /workspace; \
    install -d -m 0755 -o "$PROJECT_USER" -g "$PROJECT_USER" \
      "/home/$PROJECT_USER/.config" "/home/$PROJECT_USER/.local"; \
    printf '%s\n' '# Image-owned default; host .zshrc is an optional read-only projection.' \
      > "/home/$PROJECT_USER/.zshrc"; \
    printf '%s ALL=(ALL) NOPASSWD:ALL\n' "$PROJECT_USER" \
      > "/etc/sudoers.d/$PROJECT_USER"; \
    chmod 0440 "/etc/sudoers.d/$PROJECT_USER"; \
    visudo --check --file="/etc/sudoers.d/$PROJECT_USER"; \
    chown "$PROJECT_USER:$PROJECT_USER" "/home/$PROJECT_USER/.zshrc"; \
    test "$(id -u "$PROJECT_USER")" = "$PROJECT_UID"; \
    test "$(id -g "$PROJECT_USER")" = "$PROJECT_GID"

WORKDIR /workspace
EXPOSE 8888
CMD ["/bin/zsh"]
USER project

# The default target is deliberately CPU/LSP-only. GPU capability is opt-in via
# `--target gpu-runtime` (or docker/packs/gpu-admission.toml) and never enters
# the default image layers.

FROM cpu-runtime AS gpu-runtime

ARG CUDA_KEYRING_URL=https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
ARG CUDA_KEYRING_SHA256=d93190d50b98ad4699ff40f4f7af50f16a76dac3bb8da1eaaf366d47898ff8df

ENV PATH=/usr/local/cuda/bin:/usr/local/bin:${PATH} \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64

# NVIDIA's official Ubuntu 22.04 repository supplies toolkit/runtime libraries
# only to this explicit target. The host owns the NVIDIA kernel driver.
USER root
RUN set -eux; \
    keyring_deb="/tmp/cuda-keyring.deb"; \
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

# Keep GPU admission non-root and preserve the same project identity as CPU.
USER project

# No-target builds terminate at this CPU-only stage. This explicit final stage
# keeps Docker's default target independent from the optional GPU target.
FROM cpu-runtime AS default-runtime
USER project
