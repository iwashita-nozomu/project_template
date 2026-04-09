#!/usr/bin/env bash
set -euo pipefail

python3 tools/ci/render_devcontainer_compose.py --pack docker/packs/default.toml --output .devcontainer/docker-compose.generated.yml
