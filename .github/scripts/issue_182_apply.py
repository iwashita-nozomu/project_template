#!/usr/bin/env python3
"""Apply the one-time responsibility-boundary migration for Issue #182."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def remove_path(relative: str) -> None:
    path = ROOT / relative
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()


# Agent definitions and their template-owned maintenance machinery are not
# project-template responsibilities.
remove_path(".codex/agents")
remove_path("agent-canon-static-seed.json")
remove_path("tools/import_agent_canon_static_seed.py")
remove_path("documents/design/template-static-seed-import.md")

for path in sorted(ROOT.rglob("*"), reverse=True):
    if ".git" in path.parts:
        continue
    lowered = path.as_posix().lower()
    if "static-seed" not in lowered and "static_seed" not in lowered:
        continue
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()

(ROOT / ".codex").mkdir(parents=True, exist_ok=True)
(ROOT / ".codex/config.toml").write_text(
    """# Project-scoped Codex session settings.\n"
    "# Agent roles, prompts, profiles, skill bindings, and subagent registration\n"
    "# are supplied by the active AgentCanon/Codex runtime and are not tracked here.\n"
    "\n"
    "approval_policy = \"on-request\"\n"
    "sandbox_mode = \"workspace-write\"\n"
    "\n"
    "model = \"gpt-5.6-sol\"\n"
    "model_reasoning_effort = \"high\"\n"
    "review_model = \"gpt-5.6-luna\"\n"
    "model_context_window = 1000000\n"
    "tool_output_token_limit = 4096\n"
    """,
    encoding="utf-8",
)

checker = r'''#!/usr/bin/env python3
"""Validate that the template owns no Agent runtime definitions."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import object as _object


@dataclass(frozen=True)
class Entry:
    mode: str
    path: str


FORBIDDEN_TRACKED_PREFIXES = (
    ".gitmodules",
    ".agent-canon/update-state.toml",
    ".codex/agents",
    ".github/scripts/checkout_agent_canon_submodule.sh",
    ".github/workflows/agent-coordination.yml",
    ".github/workflows/agent-improvement-guide.yml",
    "agent-canon-static-seed.json",
    "documents/design/template-static-seed-import.md",
    "tests/fixtures/static-seed",
    "tools/agent-canon",
    "tools/import_agent_canon_static_seed.py",
    "vendor/agent-canon",
)

REQUIRED_REGULAR_FILES = ("AGENTS.md", ".codex/config.toml")

FORBIDDEN_CONFIG_KEYS = {
    "agents",
    "capsule_schema_id",
    "config_file",
    "developer_instructions",
    "logical_role_id",
    "nickname_candidates",
    "profile_id",
    "role_contract_ref",
}

EXECUTION_PATHS = (
    "Makefile",
    "README.md",
    "QUICK_START.md",
    "pyproject.toml",
    "scripts/",
    "docker/",
    ".devcontainer/",
    ".codex/",
    ".github/workflows/",
    ".github/scripts/",
    ".vscode/",
    "documents/contracts/template-bootstrap.md",
    "documents/contracts/template-validation.md",
    "documents/design/docker-zero-build-environment.md",
)

FORBIDDEN_RUNTIME_TEXT = (
    "vendor/agent-canon",
    "tools/agent-canon",
    "agent-canon-static-seed",
    "import_agent_canon_static_seed",
    "template-static-seed-import",
    "consumer-static",
    ".codex/agents",
    "AGENT_CANON_READ_TOKEN",
    "AGENT_CANON_REPO_TOKEN",
    "AGENT_CANON_REPO_SSH_KEY",
    "AGENT_CANON_TEMPLATE_SUBMODULE_STRATEGY",
    "submodule_strategy",
    "agent-canon-update",
    "agent-canon-latest-check",
    "agent_canon_source_root",
    "checkout_agent_canon_submodule",
    "PYTHONPATH=vendor/agent-canon",
    ".agent-canon/docker-compose.generated.yml",
)

SCAN_EXCLUSIONS = {
    "tools/check_runtime_independence.py",
    "tools/check_fresh_clone.sh",
    "docker/check_zero_build_contract.sh",
}


def fail(message: str) -> None:
    print(f"RUNTIME_INDEPENDENCE_FINDING={message}", file=sys.stderr)
    raise SystemExit(1)


def git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail(f"git-command-failed:{' '.join(args)}:{result.stderr.strip()}")
    return result.stdout


def tracked_entries(root: Path) -> list[Entry]:
    output = git(root, "ls-files", "-s", "-z")
    entries: list[Entry] = []
    for record in output.split("\0"):
        if not record:
            continue
        metadata, path = record.split("\t", 1)
        entries.append(Entry(mode=metadata.split(" ", 1)[0], path=path))
    return entries


def matches_prefix(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(f"{prefix}/")


def is_execution_path(path: str) -> bool:
    return any(path == prefix or path.startswith(prefix) for prefix in EXECUTION_PATHS)


def validate_tree(root: Path, entries: list[Entry]) -> None:
    by_path = {entry.path: entry for entry in entries}
    for entry in entries:
        for forbidden in FORBIDDEN_TRACKED_PREFIXES:
            if matches_prefix(entry.path, forbidden):
                fail(f"forbidden-tracked-path:{entry.path}")

    gitlinks = [entry.path for entry in entries if entry.mode == "160000"]
    if gitlinks:
        fail(f"gitlink-forbidden:{gitlinks[0]}")

    for entry in entries:
        if entry.mode != "120000":
            continue
        target = (root / entry.path).readlink().as_posix()
        if "agent-canon" in target.casefold():
            fail(f"runtime-symlink-forbidden:{entry.path}:{target}")

    for path in REQUIRED_REGULAR_FILES:
        entry = by_path.get(path)
        if entry is None:
            fail(f"required-project-file-missing:{path}")
        if entry.mode not in {"100644", "100755"}:
            fail(f"required-project-file-not-regular:{path}:{entry.mode}")


def validate_config_value(value: _object, location: str) -> None:
    if isinstance(value, dict):
        for raw_key, nested in value.items():
            key = str(raw_key)
            if key.casefold() in FORBIDDEN_CONFIG_KEYS:
                fail(f"agent-definition-config-key:{location}.{key}")
            validate_config_value(nested, f"{location}.{key}")
        return
    if isinstance(value, list):
        for index, nested in enumerate(value):
            validate_config_value(nested, f"{location}[{index}]")
        return
    if isinstance(value, str):
        normalized = value.replace("\\", "/").casefold()
        if ".codex/agents" in normalized or normalized.startswith("agents/"):
            fail(f"agent-definition-config-reference:{location}:{value}")


def validate_codex_session_config(root: Path) -> None:
    path = root / ".codex/config.toml"
    try:
        with path.open("rb") as stream:
            config = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        fail(f"codex-session-config-invalid:{exc}")
    validate_config_value(config, "config")


def validate_execution_text(root: Path, entries: list[Entry]) -> None:
    for entry in entries:
        if entry.path in SCAN_EXCLUSIONS or entry.mode not in {"100644", "100755"}:
            continue
        if not is_execution_path(entry.path):
            continue
        path = root / entry.path
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for token in FORBIDDEN_RUNTIME_TEXT:
            if token in text:
                fail(f"forbidden-runtime-reference:{entry.path}:{token}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    if not (root / ".git").exists():
        fail(f"not-a-git-worktree:{root}")
    entries = tracked_entries(root)
    validate_tree(root, entries)
    validate_codex_session_config(root)
    validate_execution_text(root, entries)
    print("RUNTIME_INDEPENDENCE=pass")


if __name__ == "__main__":
    main()
'''
# Remove a typing-import trick unsupported by static type checkers while keeping
# the validator dependency-free.
checker = checker.replace("from typing import object as _object\n", "")
checker = checker.replace("value: _object", "value: object")
(ROOT / "tools/check_runtime_independence.py").write_text(checker, encoding="utf-8")

focused_tests = r'''from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

CHECKER = Path(__file__).resolve().parents[2] / "tools/check_runtime_independence.py"
BASE_CONFIG = """approval_policy = \"on-request\"\nsandbox_mode = \"workspace-write\"\nmodel = \"gpt-5.6-sol\"\n"""


def write(root: Path, relative: str, content: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def init_repo(tmp_path: Path, config: str = BASE_CONFIG) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    write(root, "AGENTS.md", "# Project reader map\n")
    write(root, ".codex/config.toml", config)
    write(root, "Makefile", "test:\n\t@true\n")
    write(root, "README.md", "# Project\n")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    return root


def run_checker(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        check=False,
        capture_output=True,
        text=True,
    )


def stage(root: Path) -> None:
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)


def test_clean_project_session_config_passes(tmp_path: Path) -> None:
    result = run_checker(init_repo(tmp_path))
    assert result.returncode == 0, result.stderr


def test_nested_project_session_table_passes(tmp_path: Path) -> None:
    config = BASE_CONFIG + "\n[features]\nweb_search = true\n"
    result = run_checker(init_repo(tmp_path, config))
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "relative",
    [
        ".codex/agents/reviewer.toml",
        "agent-canon-static-seed.json",
        "tools/import_agent_canon_static_seed.py",
        "documents/design/template-static-seed-import.md",
        "tests/fixtures/static-seed-example/payload.toml",
    ],
)
def test_agent_definition_surfaces_are_forbidden(tmp_path: Path, relative: str) -> None:
    root = init_repo(tmp_path)
    write(root, relative, "owned_by = \"wrong_repository\"\n")
    stage(root)
    result = run_checker(root)
    assert result.returncode == 1
    assert "forbidden-tracked-path" in result.stderr


@pytest.mark.parametrize(
    "config, finding",
    [
        (BASE_CONFIG + "\n[agents]\nmax_threads = 4\n", "agent-definition-config-key"),
        (BASE_CONFIG + "\n[role]\nconfig_file = \"agents/reviewer.toml\"\n", "agent-definition-config-key"),
        (BASE_CONFIG + "\n[role]\ndeveloper_instructions = \"review\"\n", "agent-definition-config-key"),
        (BASE_CONFIG + "\nrole_path = \".codex/agents/reviewer.toml\"\n", "agent-definition-config-reference"),
    ],
)
def test_agent_registration_config_is_forbidden(
    tmp_path: Path, config: str, finding: str
) -> None:
    result = run_checker(init_repo(tmp_path, config))
    assert result.returncode == 1
    assert finding in result.stderr


@pytest.mark.parametrize("relative", ["AGENTS.md", ".codex/config.toml"])
def test_required_project_files_must_exist(tmp_path: Path, relative: str) -> None:
    root = init_repo(tmp_path)
    (root / relative).unlink()
    stage(root)
    result = run_checker(root)
    assert result.returncode == 1
    assert "required-project-file-missing" in result.stderr


def test_malformed_session_toml_fails_closed(tmp_path: Path) -> None:
    result = run_checker(init_repo(tmp_path, "[broken\n"))
    assert result.returncode == 1
    assert "codex-session-config-invalid" in result.stderr


@pytest.mark.parametrize("token", ["vendor/agent-canon", "agent-canon-update"])
def test_execution_paths_reject_live_runtime_routes(tmp_path: Path, token: str) -> None:
    root = init_repo(tmp_path)
    write(root, "Makefile", f"test:\n\t@echo '{token}'\n")
    stage(root)
    result = run_checker(root)
    assert result.returncode == 1
    assert "forbidden-runtime-reference" in result.stderr


def test_agentcanon_symlink_is_forbidden(tmp_path: Path) -> None:
    root = init_repo(tmp_path)
    link = root / "runtime-link"
    link.symlink_to("../agent-canon")
    stage(root)
    result = run_checker(root)
    assert result.returncode == 1
    assert "runtime-symlink-forbidden" in result.stderr


def test_untracked_agent_directory_does_not_change_tracked_contract(tmp_path: Path) -> None:
    root = init_repo(tmp_path)
    write(root, ".codex/agents/local-only.toml", "name = \"local\"\n")
    result = run_checker(root)
    assert result.returncode == 0, result.stderr
'''
(ROOT / "tests/tools").mkdir(parents=True, exist_ok=True)
(ROOT / "tests/tools/test_check_runtime_independence.py").write_text(
    focused_tests,
    encoding="utf-8",
)

fresh_clone = r'''#!/usr/bin/env bash
set -euo pipefail

SOURCE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMP_ROOT="$(mktemp -d)"
trap 'rm -rf "${TEMP_ROOT}"' EXIT
CLONE_ROOT="${TEMP_ROOT}/project-template"

# Exercise only the committed template tree. No AgentCanon checkout, package,
# generated registry, or network updater is part of descendant bootstrap.
git clone --quiet --no-local "${SOURCE_ROOT}" "${CLONE_ROOT}"
git -C "${CLONE_ROOT}" checkout --quiet --detach "$(git -C "${SOURCE_ROOT}" rev-parse HEAD)"

[[ ! -e "${CLONE_ROOT}/.codex/agents" ]]
[[ ! -e "${CLONE_ROOT}/agent-canon-static-seed.json" ]]
[[ ! -e "${CLONE_ROOT}/tools/import_agent_canon_static_seed.py" ]]

python3 "${CLONE_ROOT}/tools/check_runtime_independence.py" --root "${CLONE_ROOT}"
make -C "${CLONE_ROOT}" pr-check

if [[ "${TEMPLATE_FRESH_CLONE_RUN_DOCKER:-0}" == "1" ]]; then
  make -C "${CLONE_ROOT}" docker-check
  make -C "${CLONE_ROOT}" docker-build-check
fi

printf '%s\n' 'FRESH_CLONE_ACCEPTANCE=pass'
'''
(ROOT / "tools/check_fresh_clone.sh").write_text(fresh_clone, encoding="utf-8")
(ROOT / "tools/check_fresh_clone.sh").chmod(0o755)

# Remove historical documentation sections that made the template a second
# owner of Agent runtime definitions. Durable GitHub Issues retain the history.
DOC_TOKENS = (
    "agent-canon-static-seed",
    "import_agent_canon_static_seed",
    "template-static-seed-import",
    "consumer-static",
    ".codex/agents",
    "static seed",
    "static-seed",
)


def strip_markdown(text: str) -> str:
    lines = text.splitlines()
    output: list[str] = []
    skip_level: int | None = None
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            heading = stripped[level:].strip().casefold()
            if skip_level is not None and level <= skip_level:
                skip_level = None
            if skip_level is None and any(token in heading for token in DOC_TOKENS):
                skip_level = level
                continue
        if skip_level is not None:
            continue
        lowered = line.casefold()
        if any(token in lowered for token in DOC_TOKENS):
            continue
        output.append(line)
    while output and not output[-1].strip():
        output.pop()
    return "\n".join(output) + "\n"


for path in ROOT.rglob("*.md"):
    if ".git" in path.parts:
        continue
    path.write_text(strip_markdown(path.read_text(encoding="utf-8")), encoding="utf-8")

boundary = """
## Agent runtime ownership boundary

This template owns project source, build, test, runtime, and project-scoped
Codex session settings. Agent roles, prompts, model profiles, Skill bindings,
spawn routing, and write authority remain owned by AgentCanon and the active
runtime. The template does not snapshot, import, register, or validate an Agent
inventory. Adding or removing an Agent in AgentCanon therefore produces no
tracked template change.
"""
for relative in (
    "README.md",
    "documents/contracts/template-bootstrap.md",
    "documents/contracts/template-validation.md",
):
    path = ROOT / relative
    if not path.is_file():
        continue
    text = path.read_text(encoding="utf-8").rstrip() + "\n"
    if "## Agent runtime ownership boundary" not in text:
        text += boundary
    path.write_text(text, encoding="utf-8")

# No stale ownership prose may remain outside the dedicated structural guards.
allowed_residuals = {
    ROOT / "tools/check_runtime_independence.py",
    ROOT / "tools/check_fresh_clone.sh",
    ROOT / "tests/tools/test_check_runtime_independence.py",
    Path(__file__).resolve(),
    ROOT / ".github/scripts/issue_182_migrate.py",
}
for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts or path in allowed_residuals:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    lowered = text.casefold()
    residual = [token for token in DOC_TOKENS if token in lowered]
    if residual:
        raise SystemExit(f"stale Agent-definition ownership reference: {path}: {residual}")

print("ISSUE_182_MIGRATION=applied")
