"""Focused tests for canonical image ownership of the environment."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKER = PROJECT_ROOT / "tools/check_environment_contract.py"


def canonical_dockerfile() -> str:
    """Return the minimal contract-compliant Dockerfile fixture."""

    return """\
FROM node:22@sha256:aaa AS node-provider
FROM ubuntu:22.04@sha256:bbb AS cpu-runtime
COPY --from=node-provider /usr/local/bin/node /usr/local/bin/node
RUN python3 -m venv /opt/project-venv
COPY docker/requirements.txt /tmp/requirements.txt
COPY docker/requirements-gpu.txt /tmp/requirements-gpu.txt
RUN /opt/project-venv/bin/python -m pip install --require-hashes -r /tmp/requirements.txt
RUN npm install --global @openai/codex@0.145.0 bash-language-server@5.6.0
ENV PYTHONPATH=/workspace/project/python:/workspace/project VALIDATION_IMAGE=1
USER project
FROM cpu-runtime AS gpu-runtime
FROM cpu-runtime AS cpu-dev
FROM gpu-runtime AS gpu-dev
FROM cpu-dev AS cpu-validation
COPY tools/check_environment_contract.py /workspace/project/tools/check_environment_contract.py
FROM cpu-dev AS default-runtime
USER project
"""


def make_fixture(tmp_path: Path) -> Path:
    """Create a minimal repository satisfying the ownership contract."""

    root = tmp_path / "fixture"
    for directory in (
        "tools",
        "docker",
        ".devcontainer",
        ".github/workflows",
        "scripts",
    ):
        (root / directory).mkdir(parents=True, exist_ok=True)
    shutil.copy2(CHECKER, root / "tools/check_environment_contract.py")
    (root / "docker/Dockerfile").write_text(canonical_dockerfile(), encoding="utf-8")
    (root / "docker/requirements.txt").write_text("", encoding="utf-8")
    (root / "docker/requirements-gpu.txt").write_text("", encoding="utf-8")
    (root / ".devcontainer/devcontainer.json").write_text(
        json.dumps(
            {
                "build": {"dockerfile": "../docker/Dockerfile", "target": "cpu-dev"},
                "remoteUser": "project",
                "containerUser": "project",
                "workspaceFolder": "/workspace/project",
                "customizations": {
                    "vscode": {
                        "settings": {
                            "python.defaultInterpreterPath": "/opt/project-venv/bin/python"
                        }
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    (root / ".github/workflows/ci.yml").write_text(
        "\n".join(
            (
                "docker/Dockerfile",
                "--target cpu-dev",
                "tools/validation_routing.py plan",
                "tools/validation_routing.py run",
                "--plan-file .state/validation-plan.json",
                "PROJECT_TEMPLATE_IMAGE=1",
            )
        ),
        encoding="utf-8",
    )
    (root / "Makefile").write_text(
        "package:\n\tpython -m build --no-isolation\n", encoding="utf-8"
    )
    return root


def check(root: Path) -> subprocess.CompletedProcess[str]:
    """Run the checker against a fixture."""

    return subprocess.run(
        ["python3", str(root / "tools/check_environment_contract.py"), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )


def test_canonical_image_projection_passes(tmp_path: Path) -> None:
    result = check(make_fixture(tmp_path))
    assert result.returncode == 0, result.stderr
    assert "ENVIRONMENT_CONTRACT=pass" in result.stdout


def test_devcontainer_feature_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    path = root / ".devcontainer/devcontainer.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["features"] = {"ghcr.io/devcontainers/features/node:1": {}}
    path.write_text(json.dumps(payload), encoding="utf-8")
    result = check(root)
    assert result.returncode == 1
    assert "devcontainer-lifecycle-mutation-keys:features" in result.stderr


def test_workflow_dependency_install_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    path = root / ".github/workflows/ci.yml"
    path.write_text(path.read_text(encoding="utf-8") + "\nrun: pip install pytest\n", encoding="utf-8")
    result = check(root)
    assert result.returncode == 1
    assert "dependency-mutation-outside-dockerfile" in result.stderr


def test_legacy_installer_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    (root / "docker/install_python_dependencies.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    result = check(root)
    assert result.returncode == 1
    assert "legacy-installer-present:docker/install_python_dependencies.sh" in result.stderr


def test_missing_image_owned_venv_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    path = root / "docker/Dockerfile"
    path.write_text(
        path.read_text(encoding="utf-8").replace("python3 -m venv /opt/project-venv", "true"),
        encoding="utf-8",
    )
    result = check(root)
    assert result.returncode == 1
    assert "docker-capability-missing:python3 -m venv /opt/project-venv" in result.stderr


def test_isolated_package_build_is_rejected(tmp_path: Path) -> None:
    root = make_fixture(tmp_path)
    (root / "Makefile").write_text("package:\n\tpython -m build\n", encoding="utf-8")
    result = check(root)
    assert result.returncode == 1
    assert "package-build-isolation-forbidden" in result.stderr
