#!/usr/bin/env python3
"""Enforce Dockerfile ownership of the standard development environment."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path

CANONICAL_DOCKERFILE = Path("docker/Dockerfile")
DEVCONTAINER = Path(".devcontainer/devcontainer.json")
WORKFLOW = Path(".github/workflows/ci.yml")
REMOVED_INSTALLERS = (
    Path("docker/install_python_dependencies.sh"),
    Path(".devcontainer/post-create-parent.sh"),
)
REQUIRED_STAGES = (
    "cpu-runtime",
    "gpu-runtime",
    "cpu-dev",
    "gpu-dev",
    "cpu-validation",
    "default-runtime",
)

# These operations mutate the dependency environment and are therefore only
# valid in docker/Dockerfile. Keep the scan deliberately limited to executable
# orchestration surfaces so prose can explain the policy without false hits.
MUTATING_PATTERNS = (
    re.compile(r"(?:^|[;&|]\s*|\bsudo\s+)(?:apt|apt-get)\s+(?:install|upgrade)\b"),
    re.compile(r"\bpython(?:3(?:\.\d+)?)?\s+-m\s+(?:pip|venv)\b"),
    re.compile(r"\bpip(?:3(?:\.\d+)?)?\s+install\b"),
    re.compile(r"\b(?:npm|pnpm|yarn)\s+(?:install|add|ci)\b"),
    re.compile(r"\bpipx\s+install\b"),
    re.compile(r"\buv\s+(?:pip\s+install|sync)\b"),
)
SCAN_ROOTS = (
    Path(".github/workflows"),
    Path(".devcontainer"),
    Path("docker/packs"),
    Path("scripts"),
)
SCAN_FILES = (Path("Makefile"),)
SCAN_EXCLUSIONS = {
    CANONICAL_DOCKERFILE,
    Path("tools/check_environment_contract.py"),
    Path("docker/check_zero_build_contract.sh"),
}


class ContractError(RuntimeError):
    """Report an environment ownership violation."""


def fail(message: str) -> None:
    """Emit a stable machine-readable finding and stop."""

    raise ContractError(message)


def read_text(root: Path, relative: Path) -> str:
    """Read a required UTF-8 repository file."""

    path = root / relative
    if not path.is_file():
        fail(f"required-file-missing:{relative.as_posix()}")
    return path.read_text(encoding="utf-8")


def validate_dockerfile(root: Path) -> None:
    """Validate capabilities and stages owned by the canonical Dockerfile."""

    text = read_text(root, CANONICAL_DOCKERFILE)
    lowered = text.lower()
    for stage in REQUIRED_STAGES:
        if re.search(rf"\bas\s+{re.escape(stage)}\b", lowered) is None:
            fail(f"docker-stage-missing:{stage}")

    required_fragments = (
        " AS node-provider",
        "@sha256:",
        "COPY --from=node-provider",
        "python3 -m venv /opt/project-venv",
        "pip install --require-hashes",
        "COPY docker/requirements.txt",
        "COPY docker/requirements-gpu.txt",
        "npm install --global",
        "@openai/codex@0.145.0",
        "bash-language-server@5.6.0",
        "PYTHONPATH=/workspace/project/python:/workspace/project",
        "USER project",
        "VALIDATION_IMAGE=1",
    )
    for fragment in required_fragments:
        if fragment not in text:
            fail(f"docker-capability-missing:{fragment}")

    if "pip install -e" in lowered or "pip install --editable" in lowered:
        fail("docker-editable-install-forbidden")
    if re.search(r"\bfrom\s+[^\n]+\bas\s+node-provider\b", lowered) is None:
        fail("node-provider-stage-invalid")
    if text.count("@sha256:") < 2:
        fail("base-image-digest-count")


def validate_devcontainer(root: Path) -> None:
    """Validate that Dev Container only projects the canonical image."""

    raw = json.loads(read_text(root, DEVCONTAINER))
    build = raw.get("build")
    if not isinstance(build, dict):
        fail("devcontainer-build-missing")
    if build.get("dockerfile") != "../docker/Dockerfile":
        fail("devcontainer-dockerfile-not-canonical")
    if build.get("target") != "cpu-dev":
        fail("devcontainer-target-not-cpu-dev")
    if raw.get("remoteUser") != "project" or raw.get("containerUser") != "project":
        fail("devcontainer-user-not-project")
    if raw.get("workspaceFolder") != "/workspace/project":
        fail("devcontainer-workspace-not-fixed")

    forbidden_keys = {
        "features",
        "initializeCommand",
        "onCreateCommand",
        "updateContentCommand",
        "postCreateCommand",
        "postStartCommand",
        "postAttachCommand",
    }
    present = sorted(forbidden_keys.intersection(raw))
    if present:
        fail(f"devcontainer-lifecycle-mutation-keys:{','.join(present)}")

    customizations = raw.get("customizations")
    if not isinstance(customizations, dict):
        fail("devcontainer-customizations-missing")
    vscode = customizations.get("vscode")
    if not isinstance(vscode, dict):
        fail("devcontainer-vscode-customization-missing")
    settings = vscode.get("settings")
    if not isinstance(settings, dict):
        fail("devcontainer-settings-missing")
    if settings.get("python.defaultInterpreterPath") != "/opt/project-venv/bin/python":
        fail("devcontainer-python-not-image-owned")


def executable_files(root: Path) -> Iterable[Path]:
    """Yield orchestration files whose dependency mutation is forbidden."""

    for relative in SCAN_FILES:
        path = root / relative
        if path.is_file():
            yield relative
    for scan_root in SCAN_ROOTS:
        absolute = root / scan_root
        if not absolute.exists():
            continue
        for path in sorted(absolute.rglob("*")):
            if path.is_file():
                yield path.relative_to(root)


def validate_external_orchestration(root: Path) -> None:
    """Reject dependency installation outside the canonical Dockerfile."""

    for removed in REMOVED_INSTALLERS:
        if (root / removed).exists():
            fail(f"legacy-installer-present:{removed.as_posix()}")

    makefile = read_text(root, Path("Makefile"))
    if "-m build" in makefile and "--no-isolation" not in makefile:
        fail("package-build-isolation-forbidden:Makefile")

    for relative in executable_files(root):
        if relative in SCAN_EXCLUSIONS:
            continue
        path = root / relative
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            for pattern in MUTATING_PATTERNS:
                if pattern.search(stripped):
                    fail(
                        "dependency-mutation-outside-dockerfile:"
                        f"{relative.as_posix()}:{line_number}:{pattern.pattern}"
                    )


def validate_workflow(root: Path) -> None:
    """Validate that GitHub Actions builds and runs only the canonical image."""

    text = read_text(root, WORKFLOW)
    required_fragments = (
        "docker/Dockerfile",
        "--target cpu-dev",
        "tools/validation_routing.py plan",
        "tools/validation_routing.py run",
        "--plan-file .state/validation-plan.json",
        "PROJECT_TEMPLATE_IMAGE=1",
    )
    for fragment in required_fragments:
        if fragment not in text:
            fail(f"workflow-canonical-image-fragment-missing:{fragment}")
    for forbidden in (
        "actions/setup-python",
        "actions/setup-node",
        "docker/install_python_dependencies.sh",
        ".devcontainer/post-create-parent.sh",
    ):
        if forbidden in text:
            fail(f"workflow-host-environment-forbidden:{forbidden}")


def main() -> int:
    """Run all contract checks."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        validate_dockerfile(root)
        validate_devcontainer(root)
        validate_external_orchestration(root)
        validate_workflow(root)
    except (ContractError, OSError, json.JSONDecodeError) as error:
        print(f"ENVIRONMENT_CONTRACT_FINDING={error}", file=sys.stderr)
        return 1
    print("ENVIRONMENT_CONTRACT=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
