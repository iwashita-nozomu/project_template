"""Focused static checks for the CPU default and explicit GPU environment contract."""

from __future__ import annotations

import json
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_default_and_gpu_selectors_are_regular_and_identity_stable() -> None:
    """Selectors are parent-owned regular files with one canonical runtime user."""
    default_path = ROOT / ".devcontainer/devcontainer.json"
    gpu_path = ROOT / ".devcontainer/gpu-admission/devcontainer.json"
    assert default_path.is_file() and not default_path.is_symlink()
    assert gpu_path.is_file() and not gpu_path.is_symlink()
    default = json.loads(default_path.read_text(encoding="utf-8"))
    profile = json.loads(gpu_path.read_text(encoding="utf-8"))
    for config in (default, profile):
        assert config["containerUser"] == "project"
        assert config["remoteUser"] == "project"
        assert "updateRemoteUserUID" not in config
        assert "PROJECT_UID" not in config["initializeCommand"]
        assert "PROJECT_GID" not in config["initializeCommand"]
    assert "gpu-admission" not in default["name"]
    assert "gpu-admission" in profile["name"]
    assert profile["dockerComposeFile"] != default["dockerComposeFile"]


def test_cpu_docker_target_excludes_gpu_packages() -> None:
    """The default Docker target contains no CUDA/cuDNN/NCCL installation."""
    dockerfile = (ROOT / "docker/Dockerfile").read_text(encoding="utf-8")
    cpu_text = dockerfile.split("FROM cpu-runtime AS gpu-runtime", 1)[0]
    assert not any(token in cpu_text.lower() for token in ("cuda-toolkit", "cudnn", "nccl"))
    assert "FROM cpu-runtime AS gpu-runtime" in dockerfile
    for token in ("cuda-toolkit-12-8", "libcudnn9-cuda-12", "libnccl2"):
        assert token in dockerfile.split("FROM cpu-runtime AS gpu-runtime", 1)[1]


def test_runtime_packs_split_cpu_and_gpu_capability() -> None:
    """The default pack is CPU-only while GPU capability requires a target/profile."""
    default = tomllib.loads((ROOT / "docker/packs/default.toml").read_text())
    gpu = tomllib.loads((ROOT / "docker/packs/gpu-admission.toml").read_text())
    assert "target" not in default["pack"]
    assert gpu["pack"]["target"] == "gpu-runtime"
    assert gpu["runtime"]["gpus"] == "all"
    assert gpu["runtime"]["dependency_profile"] == "gpu"


def test_parent_manifest_remains_empty_and_lsp_records_are_canonical() -> None:
    """Parent dependency ownership stays empty; AgentCanon owns the LSP set."""
    parent = tomllib.loads((ROOT / ".devcontainer/dependencies.toml").read_text())
    assert parent["records"] == []
    vendor = tomllib.loads(
        (ROOT / "vendor/agent-canon/.devcontainer/dependencies.toml").read_text()
    )
    record_ids = {record["id"] for record in vendor["records"]}
    assert record_ids >= {
        "github-cli",
        "codex-cli",
        "pyright-language-server",
        "bash-language-server",
        "jq",
        "tree",
        "clang-format",
        "clangd-language-server",
    }


def test_static_environment_contract_passes() -> None:
    """The shell checker is the focused static acceptance route."""
    result = subprocess.run(
        ["bash", "docker/check_zero_build_contract.sh"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_cold_smoke_readbacks_executor_and_bind_identity() -> None:
    """Rootful cold smoke carries host IDs into the container and reads bind ownership back."""
    smoke = (ROOT / "docker/cold-build-smoke.sh").read_text(encoding="utf-8")
    for marker in (
        '"EXPECTED_EXECUTOR_UID=${project_uid}"',
        '"EXPECTED_EXECUTOR_GID=${project_gid}"',
        'test "$(id -u)" = "${EXPECTED_EXECUTOR_UID:?}"',
        'test "$(id -g)" = "${EXPECTED_EXECUTOR_GID:?}"',
        "COLD_SMOKE_CONTAINER_READBACK=identity contract=rootful",
        "probe_relative=\".devcontainer/.cold-build-smoke-",
        "stat -c '%u' \"$probe_host\"",
        "stat -c '%g' \"$probe_host\"",
        "COLD_SMOKE_BIND_READBACK=pass contract=rootful",
        "trap cleanup_probe EXIT HUP INT TERM",
    ):
        assert marker in smoke
    assert smoke.count('{"status":"pass"') == 1
