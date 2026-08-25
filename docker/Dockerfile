FROM ubuntu:24.04@sha256:33ceb71981b602c1a7443a53469e4dba065f7503eab3078a2d7a57a2ab987517 AS project-dependencies

ARG PROJECT_UID=1000

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/opt/project-venv/bin:${PATH}

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    g++ \
    cmake \
    ninja-build \
    python3 \
    python3-venv \
 && python3 -m venv /opt/project-venv \
 && rm -rf /var/lib/apt/lists/*

COPY docker/requirements.txt /tmp/project-requirements.txt
RUN python -m pip install --no-cache-dir --require-hashes \
      --requirement /tmp/project-requirements.txt \
 && rm -f /tmp/project-requirements.txt

RUN set -eux; \
    case "$PROJECT_UID" in ''|0|0*|*[!0-9]*) echo "PROJECT_UID must be positive" >&2; exit 1 ;; esac; \
    existing_user="$(getent passwd "$PROJECT_UID" | cut -d: -f1 || true)"; \
    if [ -n "$existing_user" ]; then \
      if [ "$existing_user" != project ]; then \
        usermod --login project --home /home/project --move-home --shell /bin/bash "$existing_user"; \
      fi; \
    else \
      useradd --user-group --uid "$PROJECT_UID" --create-home --shell /bin/bash project; \
    fi; \
    project_gid="$(id -g project)"; \
    install -d -m 0755 -o project -g "$project_gid" /workspace; \
    install -d -m 0755 -o project -g "$project_gid" /home/project/.config /home/project/.local; \
    test "$(id -u project)" = "$PROJECT_UID"; \
    test "$(id -u project)" != 0

ENV HOME=/home/project

# Copy the source snapshot after the dependency layers so derived projects can
# revise product files without rebuilding their dependency installation.
COPY --chown=project . /workspace/project-template
WORKDIR /workspace/project-template
CMD ["/bin/bash"]
USER project
