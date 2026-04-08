FROM nvidia/cuda:12.2.0-devel-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive
ARG NODE_VERSION=22.14.0

# GCCやビルド系 + Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git docker.io \
    build-essential pkg-config cmake ninja-build \
    python3 python3-dev python3-pip python3-venv \
    openssh-client graphviz xz-utils \
 && rm -rf /var/lib/apt/lists/*

# Codex CLI 用の Node.js は apt repo に依存させず、公式 tarball から入れる
RUN curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz" \
    | tar -xJ --strip-components=1 -C /usr/local \
 && node --version \
 && npm --version \
 && npm install -g @openai/codex \
 && codex --version \
 && npm cache clean --force

RUN python3 -m pip install --upgrade pip

# JAXは「コンテナ内同梱CUDA/cuDNN」を使う版（localじゃない）
RUN pip install --no-cache-dir "jax[cuda12]"

# その他依存パッケージ（requirements.txt で一元管理）
COPY docker/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /workspace
ENV PYTHONPATH=/workspace/python
ENV TEMPLATE_BARE_GIT_ROOT=/mnt/git
ENV CMAKE_GENERATOR=Ninja
ENV PROJECT_TEMPLATE_CPP_BUILD_ROOT=/workspace/build/cpp
ENV PROJECT_TEMPLATE_CPP_INSTALL_ROOT=/workspace/.state/cpp-install
ENV PROJECT_TEMPLATE_JAX_EXPORT_ROOT=/workspace/.state/jax-export

# Canonical image 側で safe.directory を固定し、/mnt/git を mount した
# local bare remote への push/pull を container 内からもそのまま通す。
RUN set -eux; \
    for safe_dir in \
        /workspace \
        "${TEMPLATE_BARE_GIT_ROOT}/template.git" \
        "${TEMPLATE_BARE_GIT_ROOT}/agent-canon.git"; do \
        git config --global --add safe.directory "${safe_dir}"; \
    done

# docker CLI は同梱するが、build/run をコンテナ内から行うときは
# host socket の mount か別 daemon が必要。
RUN docker --version

CMD ["/bin/bash"]
