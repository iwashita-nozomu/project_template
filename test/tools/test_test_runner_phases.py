"""Tests for static and portable selection in the canonical test runner."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNNER = PROJECT_ROOT / "test/testrunner.sh"


def run_phase(tmp_path: Path, phase: str) -> subprocess.CompletedProcess[str]:
    """Run one phase against a two-entry temporary test list."""
    test_list = tmp_path / "testlist.toml"
    test_list.write_text(
        'format = "parent-test-list-v1"\n'
        'environment_owner = "invocation-environment"\n'
        'responsibility = "parent-repository"\n'
        '[[tests]]\nname = "static-fixture"\nphase = "static"\n'
        'command = ["python3", "-c", "print(\'STATIC_FIXTURE\')"]\n'
        'working_directory = "."\n'
        '[[tests]]\nname = "portable-fixture"\nphase = "portable"\n'
        'command = ["python3", "-c", "print(\'PORTABLE_FIXTURE\')"]\n'
        'working_directory = "."\n',
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment["TEST_LIST_PATH"] = str(test_list)
    return subprocess.run(
        ["bash", str(RUNNER), "--phase", phase],
        cwd=PROJECT_ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )


def test_static_phase_runs_only_static_entries(tmp_path: Path) -> None:
    """Static selection excludes portable product tests."""
    result = run_phase(tmp_path, "static")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "STATIC_FIXTURE" in result.stdout
    assert "PORTABLE_FIXTURE" not in result.stdout
    assert "TEST_SKIP name=portable-fixture phase=portable" in result.stdout
    assert "TEST_RUNNER_RESULT=pass count=1" in result.stdout


def test_portable_phase_runs_only_portable_entries(tmp_path: Path) -> None:
    """Portable selection excludes Git-dependent static checks."""
    result = run_phase(tmp_path, "portable")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PORTABLE_FIXTURE" in result.stdout
    assert "STATIC_FIXTURE" not in result.stdout
    assert "TEST_SKIP name=static-fixture phase=static" in result.stdout
    assert "TEST_RUNNER_RESULT=pass count=1" in result.stdout
