#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$repo_root"
image=${RUN_IMAGE:-project-template:dependencies}

docker build -f docker/Dockerfile -t "$image" .
security_options=$(docker info --format '{{json .SecurityOptions}}')
case "$security_options" in
  *'"name=rootless"'*) run_user=0:0 ;;
  *) run_user="$(id -u):$(id -g)" ;;
esac

# Container root in rootless Docker maps to the invoking host user. Rootful
# Docker instead uses the host UID/GID, keeping bind-mounted outputs writable.
exec docker run --rm -i --user "$run_user" \
  --env HOME=/tmp --env RUN_ARGS \
  --mount "type=bind,src=$repo_root,dst=/workspace/project-template" \
  --workdir /workspace/project-template \
  "$image" python tools/run_file.py "$RUN_FILE"
