"""Regression tests for the canonical GitHub workflow projection."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHECKER = PROJECT_ROOT / "tools/check_github_workflows.py"
CANONICAL_WORKFLOW = PROJECT_ROOT / ".github/workflows/ci.yml"


def fixture(tmp_path: Path) -> Path:
    """Create a minimal repository with the canonical workflow."""

    root = tmp_path / "fixture"
    (root / "tools").mkdir(parents=True)
    (root / ".github/workflows").mkdir(parents=True)
    shutil.copy2(CHECKER, root / "tools/check_github_workflows.py")
    shutil.copy2(CANONICAL_WORKFLOW, root / ".github/workflows/ci.yml")
    return root


def check(root: Path) -> subprocess.CompletedProcess[str]:
    """Run the workflow checker in a fixture."""

    return subprocess.run(
        ["python3", str(root / "tools/check_github_workflows.py"), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )


def test_canonical_workflow_passes(tmp_path: Path) -> None:
    result = check(fixture(tmp_path))
    assert result.returncode == 0, result.stderr
    assert "GITHUB_WORKFLOW_CHECK=pass" in result.stdout


def test_obsolete_docker_workflow_is_rejected(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    (root / ".github/workflows/docker-build.yml").write_text(
        "name: old\non: push\njobs: {}\n", encoding="utf-8"
    )
    result = check(root)
    assert result.returncode == 1
    assert "duplicated-docker-workflow-present" in result.stderr


def test_host_python_setup_is_rejected(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    path = root / ".github/workflows/ci.yml"
    path.write_text(path.read_text(encoding="utf-8") + "\n# actions/setup-python\n", encoding="utf-8")
    result = check(root)
    assert result.returncode == 1
    assert "host-environment-mutation" in result.stderr


def test_workflow_path_filter_is_rejected(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    path = root / ".github/workflows/ci.yml"
    text = path.read_text(encoding="utf-8").replace(
        "  pull_request:\n    branches:", "  pull_request:\n    paths: ['docs/**']\n    branches:"
    )
    path.write_text(text, encoding="utf-8")
    result = check(root)
    assert result.returncode == 1
    assert "duplicated-path-routing" in result.stderr


def test_profile_command_is_not_duplicated_in_yaml(tmp_path: Path) -> None:
    root = fixture(tmp_path)
    path = root / ".github/workflows/ci.yml"
    path.write_text(path.read_text(encoding="utf-8") + "\n# make pr-check\n", encoding="utf-8")
    result = check(root)
    assert result.returncode == 1
    assert "profile-command-duplicated-in-workflow" in result.stderr
