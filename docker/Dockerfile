# @dependency-start
# responsibility Builds the project runtime image without agent convenience tooling.
# upstream design ../vendor/agent-canon/CONTAINER_OPERATIONS.md defines Dockerfile ownership rules.
# upstream implementation register_safe_directories.sh registers dynamic Git safe directories.
# downstream implementation packs/default.toml and packs/default-host-docker.toml run container smoke checks.
# @dependency-end

FROM nvidia/cuda:12.2.0-devel-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive

# GCCやビルド系 + Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git docker.io \
    rsync \
    build-essential pkg-config cmake ninja-build \
    python3 python3-dev python3-pip python3-venv \
    openssh-client graphviz \
 && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip

# JAXは「コンテナ内同梱CUDA/cuDNN」を使う版（localじゃない）
RUN python3 -m pip install --no-cache-dir "jax[cuda12]"

COPY docker/register_safe_directories.sh /usr/local/bin/register_safe_directories
RUN chmod +x /usr/local/bin/register_safe_directories \
 && register_safe_directories /workspace

WORKDIR /workspace
ENV PYTHONPATH=/workspace/python
ENV CMAKE_GENERATOR=Ninja
ENV PROJECT_TEMPLATE_CPP_BUILD_ROOT=/workspace/build/cpp
ENV PROJECT_TEMPLATE_CPP_INSTALL_ROOT=/workspace/.state/cpp-install
ENV PROJECT_TEMPLATE_JAX_EXPORT_ROOT=/workspace/.state/jax-export

# docker CLI は同梱するが、build/run をコンテナ内から行うときは
# host socket の mount か別 daemon が必要。
RUN docker --version

CMD ["/bin/bash"]
