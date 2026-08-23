"""Tests for the exact-image lifecycle owned by docker/run-tests.sh."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RUNNER = PROJECT_ROOT / "docker/run-tests.sh"


def fake_docker(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create a stateful Docker CLI fixture and return bin, marker, and log."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    marker = tmp_path / "image-present"
    log = tmp_path / "docker.log"
    executable = bin_dir / "docker"
    executable.write_text(
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "printf '%s\\n' \"$*\" >> \"$FAKE_DOCKER_LOG\"\n"
        "if [[ \"${1:-} ${2:-}\" == 'image inspect' ]]; then\n"
        "  [[ -f \"$FAKE_DOCKER_MARKER\" ]]\n"
        "elif [[ \"${1:-}\" == build ]]; then\n"
        "  touch \"$FAKE_DOCKER_MARKER\"\n"
        "elif [[ \"${1:-}\" == run ]]; then\n"
        "  exit \"${FAKE_DOCKER_RUN_EXIT:-0}\"\n"
        "elif [[ \"${1:-} ${2:-}\" == 'image rm' ]]; then\n"
        "  rm -f \"$FAKE_DOCKER_MARKER\"\n"
        "fi\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    return bin_dir, marker, log


def run_runner(tmp_path: Path, *, run_exit: int = 0) -> subprocess.CompletedProcess[str]:
    """Run the image lifecycle with a fake Docker executable."""
    bin_dir, marker, log = fake_docker(tmp_path)
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{bin_dir}:{environment['PATH']}",
            "FAKE_DOCKER_LOG": str(log),
            "FAKE_DOCKER_MARKER": str(marker),
            "FAKE_DOCKER_RUN_EXIT": str(run_exit),
        }
    )
    return subprocess.run(
        ["bash", str(RUNNER), "--tag", "fixture:test"],
        cwd=PROJECT_ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )


def test_image_is_removed_after_success(tmp_path: Path) -> None:
    """A successful test run removes the exact image it created."""
    result = run_runner(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    assert not (tmp_path / "image-present").exists()
    log = (tmp_path / "docker.log").read_text(encoding="utf-8")
    assert "build --platform linux/amd64" in log
    assert "run --rm --platform linux/amd64 fixture:test test/testrunner.sh" in log
    assert "image rm fixture:test" in log


def test_image_is_removed_after_test_failure(tmp_path: Path) -> None:
    """A failed container test retains its exit code and removes the image."""
    result = run_runner(tmp_path, run_exit=7)
    assert result.returncode == 7
    assert not (tmp_path / "image-present").exists()
    assert "image rm fixture:test" in (tmp_path / "docker.log").read_text(
        encoding="utf-8"
    )


def test_preexisting_image_is_never_overwritten_or_removed(tmp_path: Path) -> None:
    """A caller-owned tag blocks the run before build or cleanup authority."""
    bin_dir, marker, log = fake_docker(tmp_path)
    marker.touch()
    environment = os.environ.copy()
    environment.update(
        {
            "PATH": f"{bin_dir}:{environment['PATH']}",
            "FAKE_DOCKER_LOG": str(log),
            "FAKE_DOCKER_MARKER": str(marker),
        }
    )
    result = subprocess.run(
        ["bash", str(RUNNER), "--tag", "fixture:test"],
        cwd=PROJECT_ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert marker.exists()
    assert "refusing to overwrite" in result.stderr
    assert (tmp_path / "docker.log").read_text(encoding="utf-8").splitlines() == [
        "image inspect fixture:test"
    ]
