# @dependency-start
# upstream environment README.md docker runtime guidance
# downstream implementation ../tools/ci/check_fresh_clone.sh uses rsync for workspace overlay
# downstream implementation ../tools/docker_dependency_validator.sh validates canonical image tools
# @dependency-end
FROM nvidia/cuda:12.2.0-devel-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive
ARG NODE_VERSION=22.14.0

# GCCやビルド系 + Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git docker.io \
    build-essential pkg-config cmake ninja-build \
    python3 python3-dev python3-pip python3-venv \
    openssh-client graphviz rsync xz-utils \
 && rm -rf /var/lib/apt/lists/*

# GitHub CLI は repo の PR・release 運用で使うため、GitHub CLI 公式
# apt repository から canonical image に入れる。
RUN mkdir -p -m 755 /etc/apt/keyrings \
 && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    -o /etc/apt/keyrings/githubcli-archive-keyring.gpg \
 && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
 && printf 'deb [arch=%s signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main\n' "$(dpkg --print-architecture)" \
    > /etc/apt/sources.list.d/github-cli.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends gh \
 && gh --version \
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
ENV CMAKE_GENERATOR=Ninja
ENV PROJECT_TEMPLATE_CPP_BUILD_ROOT=/workspace/build/cpp
ENV PROJECT_TEMPLATE_CPP_INSTALL_ROOT=/workspace/.state/cpp-install
ENV PROJECT_TEMPLATE_JAX_EXPORT_ROOT=/workspace/.state/jax-export

EXPOSE 8888

# Canonical image 側では workspace だけを safe.directory に固定する。
# Template / AgentCanon 固有の mirror path は documents の remote policy に置く。
RUN set -eux; \
    git config --global --add safe.directory /workspace

# docker CLI は同梱するが、build/run をコンテナ内から行うときは
# host socket の mount か別 daemon が必要。
RUN ssh -V
RUN docker --version

CMD ["/bin/bash"]
