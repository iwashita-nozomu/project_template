# @dependency-start
# contract environment
# responsibility Defines the canonical development container image.
# upstream environment README.md docker runtime guidance
# upstream design ../vendor/agent-canon/documents/design/devcontainer/parent-devcontainer-policy.md parent zsh image startup contract
# downstream implementation install_python_dependencies.sh installs Python modules after workspace mount
# downstream implementation ../tools/agent-canon/ci/check_fresh_clone.sh uses rsync for workspace overlay
# downstream implementation ../tools/agent-canon/docker_dependency_validator.sh validates canonical image tools
# @dependency-end
FROM nvidia/cuda:12.2.0-devel-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive

# GCCやビルド系 + Python 3.11
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git docker.io \
    build-essential pkg-config cmake ninja-build \
    python3.11 python3.11-dev python3.11-venv python3-venv python3-pip \
    openssh-client graphviz rsync zsh \
 && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 20 \
 && python3 --version | grep -E '^Python 3\.11\.' \
 && rm -rf /var/lib/apt/lists/*

COPY docker/register_safe_directories.sh /usr/local/bin/project-template-register-safe-directories
RUN chmod +x /usr/local/bin/project-template-register-safe-directories

WORKDIR /workspace
ENV PYTHONPATH=/workspace/python
ENV CMAKE_GENERATOR=Ninja
ENV PROJECT_TEMPLATE_CPP_BUILD_ROOT=/workspace/build/cpp
ENV PROJECT_TEMPLATE_CPP_INSTALL_ROOT=/workspace/.state/cpp-install
ENV SHELL=/bin/zsh

EXPOSE 8888

# Canonical image 側では workspace を safe.directory に固定する。
# mount 済み workspace では同じ helper が vendor 直下の directory も動的に登録する。
RUN set -eux; \
    project-template-register-safe-directories /workspace

# docker CLI は同梱するが、build/run をコンテナ内から行うときは
# host socket の mount か別 daemon が必要。
RUN ssh -V
RUN docker --version

RUN set -eux; \
    install -d -m 0755 /etc/project-template/zsh; \
    printf '%s\n' \
        'if [[ ! -f /etc/project-template/parent-environment.sh || ! -r /etc/project-template/parent-environment.sh ]]; then' \
        '  print -u2 "required parent environment mount is unavailable"' \
        '  return 1' \
        'fi' \
        'source /etc/project-template/parent-environment.sh' \
        > /etc/project-template/zsh/.zshenv; \
    chmod 0644 /etc/project-template/zsh/.zshenv

CMD ["/bin/zsh"]
