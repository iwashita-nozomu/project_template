#!/usr/bin/env python3
"""Perform focused static checks for repository-owned GitHub workflows."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FORBIDDEN_RUNTIME_REFERENCES = (
    "vendor/agent-canon",
    "tools/agent-canon",
    "AGENT_CANON_",
    "agent_canon_source_root",
    "checkout_agent_canon_submodule",
    "submodules: recursive",
)
FORBIDDEN_HOST_ENVIRONMENT = (
    "actions/setup-python",
    "actions/setup-node",
    "apt-get install",
    "pip install",
    "npm install",
    "docker/install_python_dependencies.sh",
    ".devcontainer/post-create-parent.sh",
)
REQUIRED_CI_FRAGMENTS = (
    "name: Validation Summary",
    "jobs:\n  validation:\n    name: Validation Summary",
    "runs-on: ubuntu-24.04",
    "fetch-depth: 0",
    "persist-credentials: false",
    "tools/validation_routing.py plan",
    "--plan-file .state/validation-plan.json",
    "--github-output \"$GITHUB_OUTPUT\"",
    "--target cpu-dev",
    "--file docker/Dockerfile",
    "docker run --rm --platform linux/amd64",
    "/opt/project-venv/bin/python tools/validation_routing.py run",
    "--result-file .state/validation-result.json",
    "steps.route.outputs.docker_runtime_applicable == 'true'",
    "docker/cold-build-smoke.sh",
    "actions/upload-artifact@v4",
)


class WorkflowError(RuntimeError):
    """Report an invalid repository workflow contract."""


def validate_workflows(root: Path) -> None:
    """Validate workflow structure and the canonical routing projection."""

    workflows = root / ".github/workflows"
    files = sorted([*workflows.glob("*.yml"), *workflows.glob("*.yaml")])
    if not files:
        raise WorkflowError("no-workflows")

    obsolete = workflows / "docker-build.yml"
    if obsolete.exists():
        raise WorkflowError("duplicated-docker-workflow-present:docker-build.yml")

    for path in files:
        text = path.read_text(encoding="utf-8")
        for required in ("name:", "on:", "jobs:"):
            if required not in text:
                raise WorkflowError(f"missing-key:{path.name}:{required}")
        for token in FORBIDDEN_RUNTIME_REFERENCES:
            if token in text:
                raise WorkflowError(f"forbidden-runtime-reference:{path.name}:{token}")
        for token in FORBIDDEN_HOST_ENVIRONMENT:
            if token in text:
                raise WorkflowError(f"host-environment-mutation:{path.name}:{token}")
        if re.search(r"(?m)^\s+paths(?:-ignore)?:\s*", text):
            raise WorkflowError(f"duplicated-path-routing:{path.name}")

    ci_path = workflows / "ci.yml"
    if not ci_path.is_file():
        raise WorkflowError("canonical-workflow-missing:ci.yml")
    ci = ci_path.read_text(encoding="utf-8")
    for fragment in REQUIRED_CI_FRAGMENTS:
        if fragment not in ci:
            raise WorkflowError(f"canonical-fragment-missing:{fragment}")

    if ci.count("tools/validation_routing.py plan") != 1:
        raise WorkflowError("routing-plan-count")
    if ci.count("tools/validation_routing.py run") != 1:
        raise WorkflowError("routing-run-count")
    if "make pr-check" in ci or "make fresh-clone-check" in ci:
        raise WorkflowError("profile-command-duplicated-in-workflow")
    if "jobs:\n  validation:" not in ci:
        raise WorkflowError("single-summary-job-missing")


def main() -> int:
    """Run the workflow contract checker."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        validate_workflows(args.root.resolve())
    except (OSError, WorkflowError) as error:
        print(f"WORKFLOW_FINDING={error}", file=sys.stderr)
        return 1
    print("GITHUB_WORKFLOW_CHECK=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
