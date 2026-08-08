# @dependency-start
# contract test
# responsibility Verifies Template-owned CPU/GPU environment identity and cold-smoke contracts.
# upstream implementation ../../docker/cold-build-smoke.sh performs cold image and runtime acceptance
# upstream implementation ../../.devcontainer/devcontainer.json selects the default runtime profile
# upstream implementation ../../vendor/agent-canon/.devcontainer/generate-runtime-compose.sh renders compose identity
# @dependency-end
"""Focused static checks for the CPU default and explicit GPU environment contract."""

from __future__ import annotations

import json
import os
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DISPATCHER = ROOT / "tools/agent-canon/agent_tools/agent_canon_source_root.py"


def _fake_id_path(tmp_path: Path, *, uid: int, gid: int) -> Path:
    """Create a deterministic id command for generator identity tests."""
    bin_dir = tmp_path / f"fake-id-{uid}-{gid}"
    bin_dir.mkdir()
    id_path = bin_dir / "id"
    id_path.write_text(
        "#!/bin/sh\n"
        f'if [ "$1" = "-u" ]; then printf "%s\\n" "{uid}"; exit 0; fi\n'
        f'if [ "$1" = "-g" ]; then printf "%s\\n" "{gid}"; exit 0; fi\n'
        "exit 97\n",
        encoding="utf-8",
    )
    id_path.chmod(0o755)
    return bin_dir


def _run_generator(
    *, output: Path, fake_id_path: Path, extra_env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    """Generate one compose file through the public source-root dispatcher."""
    env = os.environ.copy()
    env.pop("PROJECT_UID", None)
    env.pop("PROJECT_GID", None)
    env.pop("PROJECT_USER", None)
    env["PATH"] = f"{fake_id_path}:{env['PATH']}"
    env["AGENT_CANON_DOCKER_COMPOSE_OUTPUT"] = str(output)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [
            "python3",
            str(DISPATCHER),
            "exec",
            ".devcontainer/generate-runtime-compose.sh",
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


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
        post_create = config["postCreateCommand"]
        bootstrap = ".devcontainer/bootstrap-dependencies.sh --install-language-runtime"
        entrypoint = ".devcontainer/post-create-entrypoint.sh"
        assert post_create.count(bootstrap) == 1
        assert post_create.count(entrypoint) == 1
        assert post_create.index(bootstrap) < post_create.index(entrypoint)
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
        "--expect-non-default-id",
        "COLD_SMOKE_EXPECT_NON_DEFAULT_ID=pass",
        'test "$(id -u)" = "${EXPECTED_EXECUTOR_UID:?}"',
        'test "$(id -g)" = "${EXPECTED_EXECUTOR_GID:?}"',
        ".devcontainer/bootstrap-dependencies.sh --install-language-runtime",
        "COLD_SMOKE_CONTAINER_READBACK=identity contract=rootful",
        "probe_relative=\".devcontainer/.cold-build-smoke-",
        "stat -c '%u' \"$probe_host\"",
        "stat -c '%g' \"$probe_host\"",
        "COLD_SMOKE_BIND_READBACK=pass contract=rootful",
        "trap cleanup_probe EXIT HUP INT TERM",
    ):
        assert marker in smoke
    assert smoke.count('{"status":"pass"') == 1


def test_runtime_generator_uses_host_ids_for_cpu_and_gpu(tmp_path: Path) -> None:
    """Default and explicit GPU compose use the executor's exact host IDs."""
    fake_id = _fake_id_path(tmp_path, uid=2345, gid=3456)
    cpu_output = tmp_path / "cpu-compose.yml"
    cpu = _run_generator(output=cpu_output, fake_id_path=fake_id)
    assert cpu.returncode == 0, cpu.stdout + cpu.stderr
    cpu_text = cpu_output.read_text(encoding="utf-8")
    assert 'user: "2345:3456"' in cpu_text
    assert 'PROJECT_UID: "2345"' in cpu_text
    assert 'PROJECT_GID: "3456"' in cpu_text
    assert 'AGENT_CANON_DEPENDENCY_PROFILE: "full"' in cpu_text
    assert "target: gpu-runtime" not in cpu_text
    assert "gpus: all" not in cpu_text

    gpu_output = tmp_path / "gpu-compose.yml"
    gpu = _run_generator(
        output=gpu_output,
        fake_id_path=fake_id,
        extra_env={
            "AGENT_CANON_GPU_ADMISSION_PROFILE": "gpu-admission",
            "AGENT_CANON_OPTIONAL_MOUNTS": "shared-runtime",
            "AGENT_CANON_RUNTIME_GID": "3456",
            "AGENT_CANON_HOST_SUPPLEMENTARY_GIDS": "3456 2345",
        },
    )
    assert gpu.returncode == 0, gpu.stdout + gpu.stderr
    gpu_text = gpu_output.read_text(encoding="utf-8")
    assert 'user: "2345:3456"' in gpu_text
    assert 'PROJECT_UID: "2345"' in gpu_text
    assert 'PROJECT_GID: "3456"' in gpu_text
    assert "target: gpu-runtime" in gpu_text
    assert 'AGENT_CANON_DEPENDENCY_PROFILE: "gpu"' in gpu_text
    assert "gpus: all" in gpu_text


def test_runtime_generator_rejects_identity_overrides_and_root(tmp_path: Path) -> None:
    """The generator rejects caller-selected IDs and root executor identity."""
    fake_id = _fake_id_path(tmp_path, uid=2345, gid=3456)
    override = _run_generator(
        output=tmp_path / "override.yml",
        fake_id_path=fake_id,
        extra_env={"PROJECT_UID": "999", "PROJECT_GID": "998"},
    )
    assert override.returncode != 0
    assert "PROJECT_IDS_OVERRIDE_FORBIDDEN" in override.stderr

    fake_root_id = _fake_id_path(tmp_path, uid=0, gid=0)
    root = _run_generator(output=tmp_path / "root.yml", fake_id_path=fake_root_id)
    assert root.returncode != 0
    assert "PROJECT_IDS_MUST_BE_POSITIVE_DECIMAL" in root.stderr
