#!/usr/bin/env python3
# ruff: noqa: D100, D101, D103, D107
"""Import one AgentCanon static-seed export into the template snapshot.

This is deliberately a maintainer command.  It has no source checkout, git,
network, or credential input.  The importer validates the complete input
directory before taking the target lock and writes only the three documented
snapshot surfaces (plus its private, same-filesystem transaction journal).
"""

from __future__ import annotations

import argparse
import errno
import fcntl
import hashlib
import json
import os
import re
import secrets
import stat
import sys
import tomllib
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NoReturn, cast

PROVENANCE = "agent-canon-static-seed.json"
CONFIG = ".codex/config.toml"
ROLE_DIR = ".codex/agents"
BUDGET_KEYS = {"max_threads", "max_depth", "job_max_runtime_seconds"}
ROLE_FIELDS = {
    "name",
    "description",
    "nickname_candidates",
    "sandbox_mode",
    "approval_policy",
    "model",
    "model_reasoning_effort",
    "developer_instructions",
}
ROLE_NAME = re.compile(r"^[A-Za-z0-9_-]+$")
COMMIT = re.compile(r"^[0-9a-f]{40}$|^[0-9a-f]{64}$")
DIGEST = re.compile(r"^[0-9a-f]{64}$")
REVIEWED_SOURCE_COMMIT = "c5fa3a22c8486952dc6dede0cc3a25e5ba7741e5"
REVIEWED_PAYLOAD_MANIFEST = (
    (".codex/agents/artifact_reviewer.toml", "c5131d7cc9807dfb41535fc0424cd0e624e4dfd2320f1779ad2b4ac02ab4c4fe", 0o644),
    (".codex/agents/benchmark_reviewer.toml", "059ca570c86c2f9b34c82dcc0ea28e3fbd6cfea6da9e9aefb7e403774f698b07", 0o644),
    (".codex/agents/citation_evidence_reviewer.toml", "fa8b1337c1ec1817184c86f65270012f821db6df5847f349274619c6bd95dcda", 0o644),
    (".codex/agents/cpp_reviewer.toml", "90b18a3b36a210f1f7636b864c65d4856fdbc7ee01db88c39062585056a8678e", 0o644),
    (".codex/agents/detailed_design_reviewer.toml", "8b5cb609a0c73780962b51466c32ae7abc36ebd49352257123cb17fcace0914e", 0o644),
    (".codex/agents/detailed_designer.toml", "4e81fa2cbc1da043898fc205500cbcc19f88adf1829b4193308ea41eed88f554", 0o644),
    (".codex/agents/diff_triage_reviewer.toml", "004cfc6c48d32c0c647b61e404c0cbc377e670eece6e45368435e0b82b727fd6", 0o644),
    (".codex/agents/docs_workflow_steward.toml", "bc6f8435374802daec126f426a5f3b1d3e4df2abb634c9dfac1314edfe3de8c0", 0o644),
    (".codex/agents/document_flow_reviewer.toml", "9a6e5b2c42e8b6ec5ebc898256f7f6793f7e62f655d2137f243fe87881a389d7", 0o644),
    (".codex/agents/execution_planner.toml", "d1c30ab3770df6fe0d0b70a450736df554b6df67fd829c96b45228d6a7803f8e", 0o644),
    (".codex/agents/experiment_runner.toml", "5f7f8b9c3b8e66716e4e2f2ec54786e1558ecb292be00ead05dd9d09dac8808d", 0o644),
    (".codex/agents/explorer.toml", "46f0ee62ac7bc76a1b47ebb7cd7928a959db4af2aff31e37a06de54adcbf366d", 0o644),
    (".codex/agents/fair_data_reviewer.toml", "f5a40234912bf944c28e2f11128f64ce12c7c6789c7085f4c335cdb60851c2df", 0o644),
    (".codex/agents/literature_researcher.toml", "6d590fcb6f997dd3db86bc4f9b81495d8bdad41f75859940d48f97d06aa60136", 0o644),
    (".codex/agents/logic_gap_reviewer.toml", "783edb9f2e6a624cc3a773cce3b23089cd5621111d415a2e2c73979a0c88aa3b", 0o644),
    (".codex/agents/long_form_writer.toml", "dad2c9e24bf4e1d76b159cdae5538566b4374f61d3c60b290f48e11140232bb6", 0o644),
    (".codex/agents/manager_reviewer.toml", "6ec8ff36a679359cac87129ff142e88a2fb53e47f2689d7b37581cedc1928fde", 0o644),
    (".codex/agents/ml_science_reviewer.toml", "785559993828ce0b1c3f0afcb9dd04a5a1a5821367b9f5bdf44cf8ed1a5bca13", 0o644),
    (".codex/agents/notation_definition_reviewer.toml", "8bbb193d709359b1c760cacd312eb0953576cbb7d6df453dd51a3e2b2b84d0cb", 0o644),
    (".codex/agents/oop_readability_reviewer.toml", "fe0fcb2241db20a4214cefc7bccc996db577a2df4a0b0cd1dc224050f5190843", 0o644),
    (".codex/agents/plan_reviewer.toml", "ada47e12255d7124851753cbb73e9ed3d1a039bd1697858002ee5cf9d58573d6", 0o644),
    (".codex/agents/project_reviewer.toml", "f105ef533ce4990bfba862428d76ec426e7d98eb901963f5ce54b3040104ee1a", 0o644),
    (".codex/agents/prompt_config_reviewer.toml", "efe7fd27f09feddb79bb75a46f9c5fd5e1ded6373fc301e8c9f404919442e56b", 0o644),
    (".codex/agents/python_reviewer.toml", "3579d642431481b3b6074785bc46b8cbbdfb7332952d2e156aebf2a16a4ac3ca", 0o644),
    (".codex/agents/report_reviewer.toml", "77af640f3f8f87cbab9823ff383b257362aadf99d84c64e8b06c92f0b2544d3f", 0o644),
    (".codex/agents/reproducibility_reviewer.toml", "bc0b2ea41de98f565c9c128ac1a84def9ce54a5f5cddee209236e964dc14139b", 0o644),
    (".codex/agents/requirements_organizer.toml", "188faa829174c37623937487e0e604785fdd9c6e38a9ff14c357585f2bbb79e5", 0o644),
    (".codex/agents/reviewer.toml", "950253180103adb8dd4fa17af71e15b62d2bf05aa25dcb713742e072fcb0e131", 0o644),
    (".codex/agents/scientific_computing_reviewer.toml", "c2eef8d80ffad19da78167d5d59bd5b2df5862e4aea8cfd189fe017d9adaf35a", 0o644),
    (".codex/agents/ship_reviewer.toml", "683ef284d2fc96600fae6a2a8450680fc09dd14708c1472cf2e9b854b1aa2dc2", 0o644),
    (".codex/agents/skill_evaluator.toml", "579196b6a43d64bf2d5cefebc6c44637eeed8e8632762bb3aee368efe6189459", 0o644),
    (".codex/agents/spark_worker.toml", "8fd4bacb0a023d46b87e27ef8bd6849dd93165dc6ce6881b9af69de13eeaf88b", 0o644),
    (".codex/agents/terra.toml", "c484a834bc2b015e189114839fda23da95b1bbbdbf577ab063d33ea9d1bb1c4c", 0o644),
    (".codex/agents/test_designer.toml", "f786431a5f1a6e86dfd9469349583fe7efb0529a6d1f3780dd1a0695a67f6bfe", 0o644),
    (".codex/agents/worker.toml", "c8dc90d37ac6d7aaeb27aadb94a62d34d5b705abee2ad34155dd1c685fb6a2f4", 0o644),
    (".codex/config.toml", "d60babb9e6ba297a3178eb6878df66621b72c895f5f53ce25186b6f229435d45", 0o644),
    ("agent-canon-static-seed.json", "bd1db005e5c141b83d0495276bb173db308cb1466ebede2f6c656a697cde85d2", 0o644),
)
PREFIXES = (
    "agents/skills/",
    "agents/model_profiles.toml",
    "tools/agent_tools/",
    "../../agents/",
    "../../tools/",
)
FORBIDDEN_MARKERS = (
    "vendor/agent-canon",
    "tools/agent-canon",
    "agent_canon_source_root",
    "agent-canon-update",
    "agent-canon-latest-check",
    "git clone",
    "git submodule",
    "curl ",
    "wget ",
    "http://",
    "https://",
    "ssh://",
    "import agent_tools",
    "from agent_tools",
    "sync-state",
    "update-state",
    "agent_canon_repo_token",
    "agent_canon_read_token",
    "github_pat_",
    "authorization: bearer",
    "begin private key",
)
FORBIDDEN_TOML_KEYS = {
    "command",
    "env",
    "hooks",
    "mcp_servers",
    "network_access",
    "remote",
    "url",
    "token",
    "secret",
    "credential",
    "credentials",
    "update_state",
}
JOURNAL_PREFIX = ".static-seed-import."
JOURNAL_SUFFIX = ".txn"
CLEANUP_SUFFIX = ".cleanup"
RESTORE_DIR = "restore"


class ImportError_(Exception):
    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}{':' + detail if detail else ''}")


@dataclass(frozen=True)
class FileSnapshot:
    path: str
    data: bytes
    mode: int
    device: int
    inode: int
    size: int


@dataclass(frozen=True)
class ValidatedBundle:
    source_commit: str
    provenance: bytes
    config: bytes
    roles: dict[str, bytes]
    digest: str
    snapshots: dict[str, FileSnapshot]
    dirs: dict[str, tuple[int, int, int, tuple[tuple[str, int, int, int, int], ...]]]


@dataclass(frozen=True)
class TargetEntry:
    data: bytes | None
    mode: int | None
    device: int | None
    inode: int | None


@dataclass
class TargetHandles:
    """Stable descriptor set for the project root and controlled directories."""

    root_fd: int
    codex_fd: int
    agents_fd: int
    root_identity: tuple[int, int, int, int]
    codex_identity: tuple[int, int, int, int]
    agents_identity: tuple[int, int, int, int]

    def close(self) -> None:
        """Close the retained directory descriptors."""
        os.close(self.agents_fd)
        os.close(self.codex_fd)


Manifest = dict[str, Any]


def fail(code: str, detail: str = "") -> NoReturn:
    raise ImportError_(code, detail)


def fsync_fd(fd: int) -> None:
    os.fsync(fd)


def fsync_dir(fd: int) -> None:
    os.fsync(fd)


def lexical_absolute(raw: str) -> str:
    if "\x00" in raw:
        fail("TSSI_BUNDLE_ROOT", "nul")
    if os.path.isabs(raw):
        return raw
    return os.path.join(os.getcwd(), raw)


def open_directory_no_follow(parent_fd: int, name: str, symlink_code: str) -> int:
    """Open a directory entry without following symlinks, classifying races."""
    try:
        before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except OSError:
        raise
    if stat.S_ISLNK(before.st_mode):
        fail(symlink_code, name)
    try:
        return os.open(
            name,
            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
            dir_fd=parent_fd,
        )
    except OSError as exc:
        try:
            after = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
        except OSError:
            raise exc
        if stat.S_ISLNK(after.st_mode):
            fail(symlink_code, name)
        raise


def open_lexical_directory(raw: str) -> int:
    """Open every component without following a symlink.

    ``realpath`` is intentionally not used: the argument remains a lexical
    spelling and the resulting descriptor is the bundle identity.
    """
    path = lexical_absolute(raw)
    drive, tail = os.path.splitdrive(path)
    del drive
    components = [part for part in tail.split(os.sep) if part not in {"", "."}]
    fd = os.open(os.sep, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for component in components:
            next_fd = open_directory_no_follow(fd, component, "TSSI_BUNDLE_ROOT_SYMLINK")
            os.close(fd)
            fd = next_fd
        return fd
    except ImportError_:
        os.close(fd)
        raise
    except OSError as exc:
        os.close(fd)
        if exc.errno == errno.ELOOP:
            fail("TSSI_BUNDLE_ROOT_SYMLINK", str(exc))
        fail("TSSI_BUNDLE_ROOT", str(exc))


def safe_names(fd: int) -> list[str]:
    try:
        names = os.listdir(fd)
    except OSError as exc:
        fail("TSSI_BUNDLE_ROOT", str(exc))
    for name in names:
        if "\x00" in name or any(0xDC80 <= ord(char) <= 0xDCFF for char in name):
            fail("TSSI_BUNDLE_UNEXPECTED_PATH", "invalid-name")
    return names


def stat_at(fd: int, name: str, code: str = "TSSI_BUNDLE_UNEXPECTED_PATH") -> os.stat_result:
    try:
        return os.stat(name, dir_fd=fd, follow_symlinks=False)
    except OSError as exc:
        fail(code, f"{name}:{exc}")


def check_dir(fd: int, name: str, code: str = "TSSI_BUNDLE_SYMLINK") -> os.stat_result:
    st = stat_at(fd, name)
    if not stat.S_ISDIR(st.st_mode):
        fail(code, name)
    return st


def read_regular(fd: int, name: str, rel: str, *, bundle: bool = True) -> FileSnapshot:
    st = stat_at(fd, name)
    if bundle and stat.S_ISLNK(st.st_mode):
        fail("TSSI_BUNDLE_FILE_SYMLINK", rel)
    if not stat.S_ISREG(st.st_mode):
        fail("TSSI_BUNDLE_NONREGULAR" if bundle else "TSSI_TARGET_UNSAFE_ENTRY", rel)
    if stat.S_IMODE(st.st_mode) != 0o644:
        fail("TSSI_BUNDLE_MODE" if bundle else "TSSI_TARGET_SHAPE", rel)
    if st.st_nlink != 1:
        fail("TSSI_BUNDLE_NONREGULAR" if bundle else "TSSI_TARGET_UNSAFE_ENTRY", f"hard-link:{rel}")
    try:
        child = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
    except OSError as exc:
        fail("TSSI_BUNDLE_SYMLINK" if bundle else "TSSI_TARGET_SYMLINK", f"{rel}:{exc}")
    try:
        before = os.fstat(child)
        data = b""
        while True:
            chunk = os.read(child, 1024 * 1024)
            if not chunk:
                break
            data += chunk
        after = os.fstat(child)
    finally:
        os.close(child)
    attrs = (st.st_dev, st.st_ino, st.st_size, stat.S_IMODE(st.st_mode), st.st_nlink)
    attrs2 = (before.st_dev, before.st_ino, before.st_size, stat.S_IMODE(before.st_mode), before.st_nlink)
    attrs3 = (after.st_dev, after.st_ino, after.st_size, stat.S_IMODE(after.st_mode), after.st_nlink)
    if attrs != attrs2 or attrs2 != attrs3 or len(data) != st.st_size:
        fail("TSSI_BUNDLE_RACE" if bundle else "TSSI_TARGET_RACE", rel)
    return FileSnapshot(rel, data, stat.S_IMODE(st.st_mode), st.st_dev, st.st_ino, st.st_size)


def dir_snapshot(fd: int) -> tuple[int, int, int, tuple[tuple[str, int, int, int, int], ...]]:
    st = os.fstat(fd)
    if not stat.S_ISDIR(st.st_mode):
        fail("TSSI_BUNDLE_RACE", "directory-type")
    entries: list[tuple[str, int, int, int, int]] = []
    for name in safe_names(fd):
        item = stat_at(fd, name)
        entries.append((name, item.st_dev, item.st_ino, stat.S_IMODE(item.st_mode), stat.S_IFMT(item.st_mode)))
    return (st.st_dev, st.st_ino, stat.S_IMODE(st.st_mode), tuple(sorted(entries)))


def parse_toml(data: bytes, where: str) -> dict[str, Any]:
    try:
        parsed = tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        fail("TSSI_BUNDLE_CONFIG", f"{where}:{exc}")
    return parsed


def scan_toml_keys(value: Any, where: str) -> None:
    if isinstance(value, dict):
        mapping = cast(dict[str, Any], value)
        for key, child in mapping.items():
            if str(key).lower() in FORBIDDEN_TOML_KEYS:
                fail("TSSI_BUNDLE_FORBIDDEN_SURFACE", f"{where}:{key}")
            scan_toml_keys(child, f"{where}.{key}")
    elif isinstance(value, list):
        sequence = cast(list[Any], value)
        for index, child in enumerate(sequence):
            scan_toml_keys(child, f"{where}[{index}]")


def semantic_scan(parts: Iterable[tuple[str, bytes]]) -> None:
    for where, raw in parts:
        lowered = raw.lower()
        for prefix in PREFIXES:
            if prefix.encode() in lowered:
                fail("TSSI_BUNDLE_FORBIDDEN_PREFIX", f"{where}:{prefix}")
        for marker in FORBIDDEN_MARKERS:
            if marker.encode() in lowered:
                fail("TSSI_BUNDLE_FORBIDDEN_SURFACE", f"{where}:{marker}")


def role_names(config: dict[str, Any]) -> set[str]:
    agents_value = config.get("agents")
    if not isinstance(agents_value, dict):
        fail("TSSI_BUNDLE_CONFIG", "missing-agents")
    agents = cast(dict[str, Any], agents_value)
    result: set[str] = set()
    for name, raw_payload in agents.items():
        if name in BUDGET_KEYS:
            continue
        if not ROLE_NAME.fullmatch(name):
            fail("TSSI_BUNDLE_ROLE_CLOSURE", f"invalid-role:{name}")
        payload = cast(dict[str, Any], raw_payload) if isinstance(raw_payload, dict) else {}
        if set(payload) != {"description", "config_file"}:
            fail("TSSI_BUNDLE_CONFIG", f"agent:{name}")
        config_file = payload.get("config_file")
        if config_file != f"agents/{name}.toml":
            fail("TSSI_BUNDLE_ROLE_CLOSURE", f"path:{name}")
        if not isinstance(payload.get("description"), str):
            fail("TSSI_BUNDLE_CONFIG", f"description:{name}")
        result.add(name)
    return result


def validate_role(name: str, data: bytes) -> None:
    try:
        lines = data.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        fail("TSSI_BUNDLE_CONFIG", f"role-encoding:{name}:{exc}")
    comments = [line for line in lines if line.startswith("#")]
    if len(comments) != 2 or comments[0] != "# generated role view: generated_role_view_v1":
        fail("TSSI_BUNDLE_CONFIG", f"role-header:{name}")
    if not re.fullmatch(r"# source canonical digest: [0-9a-f]{64}", comments[1]):
        fail("TSSI_BUNDLE_CONFIG", f"role-digest:{name}")
    parsed = parse_toml(data, f"role:{name}")
    if set(parsed) != ROLE_FIELDS:
        fail("TSSI_BUNDLE_CONFIG", f"role-fields:{name}")
    if parsed.get("name") != name:
        fail("TSSI_BUNDLE_ROLE_CLOSURE", f"name:{name}")
    if not all(isinstance(parsed.get(key), str) for key in ROLE_FIELDS - {"nickname_candidates"}):
        fail("TSSI_BUNDLE_CONFIG", f"role-types:{name}")
    if not isinstance(parsed.get("nickname_candidates"), list) or not all(
        isinstance(item, str) for item in parsed["nickname_candidates"]
    ):
        fail("TSSI_BUNDLE_CONFIG", f"nickname-types:{name}")
    scan_toml_keys(parsed, f"role:{name}")


def validate_provenance(data: bytes) -> str:
    try:
        text = data.decode("utf-8")
        obj = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        fail("TSSI_BUNDLE_PROVENANCE", str(exc))
    if not isinstance(obj, dict):
        fail("TSSI_BUNDLE_PROVENANCE", "object")
    obj = cast(dict[str, Any], obj)
    if set(obj) != {"schema_version", "source_commit", "source_repository"}:
        fail("TSSI_BUNDLE_PROVENANCE", "keys")
    if obj["schema_version"] != 1 or obj["source_repository"] != "iwashita-nozomu/agent-canon":
        fail("TSSI_BUNDLE_PROVENANCE", "value")
    commit_value = obj["source_commit"]
    if not isinstance(commit_value, str):
        fail("TSSI_BUNDLE_PROVENANCE", "commit-type")
    commit = commit_value
    if not COMMIT.fullmatch(commit):
        fail("TSSI_BUNDLE_PROVENANCE", "commit")
    expected = (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    if data != expected:
        fail("TSSI_BUNDLE_PROVENANCE", "serialization")
    return commit


def validate_reviewed_payload(commit: str, snapshots: dict[str, FileSnapshot]) -> None:
    expected_paths = {path for path, _digest, _mode in REVIEWED_PAYLOAD_MANIFEST}
    if commit != REVIEWED_SOURCE_COMMIT or set(snapshots) != expected_paths:
        fail("TSSI_BUNDLE_REVIEWED_PAYLOAD", "manifest-closure")
    for path, expected_digest, expected_mode in REVIEWED_PAYLOAD_MANIFEST:
        actual = snapshots[path]
        if actual.mode != expected_mode or hashlib.sha256(actual.data).hexdigest() != expected_digest:
            fail("TSSI_BUNDLE_REVIEWED_PAYLOAD", path)


def open_bundle_files(rootfd: int) -> ValidatedBundle:
    root_st = os.fstat(rootfd)
    if not stat.S_ISDIR(root_st.st_mode):
        fail("TSSI_BUNDLE_ROOT")
    root_names = safe_names(rootfd)
    if set(root_names) != {PROVENANCE, ".codex"}:
        fail("TSSI_BUNDLE_UNEXPECTED_PATH", ",".join(sorted(set(root_names) - {PROVENANCE, ".codex"})))
    try:
        codex_fd = open_directory_no_follow(rootfd, ".codex", "TSSI_BUNDLE_DIRECTORY_SYMLINK")
    except OSError as exc:
        fail("TSSI_BUNDLE_DIRECTORY_SYMLINK" if exc.errno == errno.ELOOP else "TSSI_BUNDLE_ROOT", str(exc))
    try:
        if set(safe_names(codex_fd)) != {"config.toml", "agents"}:
            fail("TSSI_BUNDLE_UNEXPECTED_PATH", "codex-shape")
        try:
            agents_fd = open_directory_no_follow(codex_fd, "agents", "TSSI_BUNDLE_DIRECTORY_SYMLINK")
        except OSError as exc:
            fail("TSSI_BUNDLE_DIRECTORY_SYMLINK" if exc.errno == errno.ELOOP else "TSSI_BUNDLE_ROOT", str(exc))
        try:
            initial_dirs = {
                ".": dir_snapshot(rootfd),
                ".codex": dir_snapshot(codex_fd),
                ROLE_DIR: dir_snapshot(agents_fd),
            }
            prov = read_regular(rootfd, PROVENANCE, PROVENANCE)
            cfg = read_regular(codex_fd, "config.toml", CONFIG)
            commit = validate_provenance(prov.data)
            config = parse_toml(cfg.data, CONFIG)
            scan_toml_keys(config, CONFIG)
            names = role_names(config)
            expected = {f"{name}.toml" for name in names}
            actual = set(safe_names(agents_fd))
            if actual != expected:
                fail("TSSI_BUNDLE_ROLE_CLOSURE", f"missing={sorted(expected-actual)} extra={sorted(actual-expected)}")
            roles: dict[str, bytes] = {}
            snapshots = {PROVENANCE: prov, CONFIG: cfg}
            for name in sorted(names):
                snap = read_regular(agents_fd, f"{name}.toml", f"{ROLE_DIR}/{name}.toml")
                validate_role(name, snap.data)
                roles[name] = snap.data
                snapshots[f"{ROLE_DIR}/{name}.toml"] = snap
            semantic_scan([(PROVENANCE, prov.data), (CONFIG, cfg.data), *[(f"{ROLE_DIR}/{n}.toml", d) for n, d in roles.items()]])
            validate_reviewed_payload(commit, snapshots)
            digest = hashlib.sha256(
                b"".join(snapshots[path].data for path in sorted(snapshots))
            ).hexdigest()
            dirs = {
                ".": dir_snapshot(rootfd),
                ".codex": dir_snapshot(codex_fd),
                ROLE_DIR: dir_snapshot(agents_fd),
            }
            if dirs != initial_dirs:
                fail("TSSI_BUNDLE_RACE", "directory-entries")
            return ValidatedBundle(commit, prov.data, cfg.data, roles, digest, snapshots, dirs)
        finally:
            os.close(agents_fd)
    finally:
        os.close(codex_fd)


def revalidate_bundle(rootfd: int, bundle: ValidatedBundle) -> None:
    """Re-read the descriptor-owned bundle immediately before a live write."""
    try:
        codex_fd = open_directory_no_follow(rootfd, ".codex", "TSSI_BUNDLE_DIRECTORY_SYMLINK")
    except OSError as exc:
        fail("TSSI_BUNDLE_DIRECTORY_SYMLINK" if exc.errno == errno.ELOOP else "TSSI_BUNDLE_RACE", str(exc))
    try:
        try:
            agents_fd = open_directory_no_follow(codex_fd, "agents", "TSSI_BUNDLE_DIRECTORY_SYMLINK")
        except OSError as exc:
            fail("TSSI_BUNDLE_DIRECTORY_SYMLINK" if exc.errno == errno.ELOOP else "TSSI_BUNDLE_RACE", str(exc))
        try:
            if dir_snapshot(rootfd) != bundle.dirs["."]:
                fail("TSSI_BUNDLE_RACE", "root-entries")
            if dir_snapshot(codex_fd) != bundle.dirs[".codex"]:
                fail("TSSI_BUNDLE_RACE", "codex-entries")
            if dir_snapshot(agents_fd) != bundle.dirs[ROLE_DIR]:
                fail("TSSI_BUNDLE_RACE", "role-entries")
            for rel, expected in bundle.snapshots.items():
                if rel == PROVENANCE:
                    parent, name = rootfd, PROVENANCE
                elif rel == CONFIG:
                    parent, name = codex_fd, "config.toml"
                else:
                    parent, name = agents_fd, rel.rsplit("/", 1)[1]
                actual = read_regular(parent, name, rel)
                if (actual.data, actual.mode, actual.device, actual.inode, actual.size) != (
                    expected.data, expected.mode, expected.device, expected.inode, expected.size
                ):
                    fail("TSSI_BUNDLE_RACE", rel)
        finally:
            os.close(agents_fd)
    finally:
        os.close(codex_fd)


def project_root() -> Path:
    return Path(__file__).resolve(strict=True).parents[1]


def controlled_paths(bundle: ValidatedBundle) -> list[str]:
    return [PROVENANCE, CONFIG, *[f"{ROLE_DIR}/{name}.toml" for name in sorted(bundle.roles)]]


def identity(st: os.stat_result) -> tuple[int, int, int]:
    return (st.st_dev, st.st_ino, stat.S_IFMT(st.st_mode))


def directory_identity(st: os.stat_result) -> tuple[int, int, int, int]:
    return (st.st_dev, st.st_ino, stat.S_IMODE(st.st_mode), stat.S_IFMT(st.st_mode))


def open_target_handles(rootfd: int) -> TargetHandles:
    root_st = os.fstat(rootfd)
    if not stat.S_ISDIR(root_st.st_mode):
        fail("TSSI_TARGET_SHAPE", "root")
    codex_fd = os.open(".codex", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=rootfd)
    agents_fd = -1
    try:
        codex_st = os.fstat(codex_fd)
        agents_fd = os.open("agents", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=codex_fd)
        agents_st = os.fstat(agents_fd)
    except OSError:
        if agents_fd >= 0:
            os.close(agents_fd)
        os.close(codex_fd)
        raise
    return TargetHandles(
        rootfd,
        codex_fd,
        agents_fd,
        directory_identity(root_st),
        directory_identity(codex_st),
        directory_identity(agents_st),
    )


def revalidate_target_handles(handles: TargetHandles) -> None:
    if directory_identity(os.fstat(handles.root_fd)) != handles.root_identity:
        fail("TSSI_TARGET_RACE", "root")
    if directory_identity(os.fstat(handles.codex_fd)) != handles.codex_identity:
        fail("TSSI_TARGET_RACE", "codex-fd")
    if directory_identity(os.fstat(handles.agents_fd)) != handles.agents_identity:
        fail("TSSI_TARGET_RACE", "agents-fd")
    codex_check = os.open(
        ".codex", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=handles.root_fd
    )
    try:
        if directory_identity(os.fstat(codex_check)) != handles.codex_identity:
            fail("TSSI_TARGET_RACE", "codex-entry")
        agents_check = os.open(
            "agents", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=codex_check
        )
        try:
            if directory_identity(os.fstat(agents_check)) != handles.agents_identity:
                fail("TSSI_TARGET_RACE", "agents-entry")
        finally:
            os.close(agents_check)
    finally:
        os.close(codex_check)


def parent_for(handles: TargetHandles, rel: str) -> tuple[int, str]:
    if rel == PROVENANCE:
        return handles.root_fd, PROVENANCE
    if rel == CONFIG:
        return handles.codex_fd, "config.toml"
    return handles.agents_fd, rel.rsplit("/", 1)[1]


def read_target(handles: TargetHandles, bundle: ValidatedBundle) -> dict[str, TargetEntry]:
    revalidate_target_handles(handles)
    codex_extras = set(safe_names(handles.codex_fd)) - {"config.toml", "agents"}
    for name in codex_extras:
        if name.startswith(JOURNAL_PREFIX) and (
            name.endswith(JOURNAL_SUFFIX) or name.endswith(JOURNAL_SUFFIX + CLEANUP_SUFFIX)
        ):
            continue
        fail("TSSI_TARGET_SHAPE", "codex-unknown-entry")
    for name in safe_names(handles.agents_fd):
        if not name.endswith(".toml") or "/" in name:
            fail("TSSI_TARGET_UNSAFE_ENTRY", name)
        st = stat_at(handles.agents_fd, name, "TSSI_TARGET_UNSAFE_ENTRY")
        if not stat.S_ISREG(st.st_mode) or stat.S_IMODE(st.st_mode) != 0o644 or st.st_nlink != 1:
            fail("TSSI_TARGET_UNSAFE_ENTRY", name)
    paths = {PROVENANCE, CONFIG}
    paths.update(f"{ROLE_DIR}/{name}" for name in safe_names(handles.agents_fd))
    paths.update(controlled_paths(bundle))
    state: dict[str, TargetEntry] = {}
    for rel in sorted(paths):
        parent, name = parent_for(handles, rel)
        try:
            try:
                os.stat(name, dir_fd=parent, follow_symlinks=False)
            except FileNotFoundError:
                continue
            else:
                snap = read_regular(parent, name, rel, bundle=False)
                state[rel] = TargetEntry(snap.data, snap.mode, snap.device, snap.inode)
        except OSError as exc:
            fail("TSSI_TARGET_SHAPE", f"{rel}:{exc}")
    return state


def snapshot_digest(state: dict[str, TargetEntry]) -> str:
    h = hashlib.sha256()
    for path in sorted(state):
        item = state[path]
        h.update(path.encode() + b"\0")
        h.update(item.data or b"<missing>")
        h.update(str(item.mode).encode() + b"\0")
    return h.hexdigest()


def target_lock(rootfd: int) -> TargetHandles:
    handles = open_target_handles(rootfd)
    try:
        fcntl.flock(handles.agents_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        handles.close()
        fail("TSSI_CONCURRENT_IMPORT")
    return handles


def journal_names(handles: TargetHandles) -> list[str]:
    return sorted(
        name
        for name in safe_names(handles.codex_fd)
        if name.startswith(JOURNAL_PREFIX)
        and (name.endswith(JOURNAL_SUFFIX) or name.endswith(JOURNAL_SUFFIX + CLEANUP_SUFFIX))
    )


def transaction_id_from_journal_name(name: str) -> str:
    base = name[:-len(CLEANUP_SUFFIX)] if name.endswith(CLEANUP_SUFFIX) else name
    if not base.startswith(JOURNAL_PREFIX) or not base.endswith(JOURNAL_SUFFIX):
        fail("TSSI_RECOVERY", "journal-name")
    value = base[len(JOURNAL_PREFIX) : -len(JOURNAL_SUFFIX)]
    if not re.fullmatch(r"[0-9a-f]{32}", value):
        fail("TSSI_RECOVERY", "journal-name")
    return value


def write_at(fd: int, name: str, data: bytes, mode: int = 0o600, *, exclusive: bool = True) -> dict[str, Any]:
    flags = os.O_RDWR | os.O_CLOEXEC | (os.O_CREAT | os.O_EXCL if exclusive else os.O_CREAT | os.O_TRUNC)
    child = os.open(name, flags, mode, dir_fd=fd)
    try:
        # Creation mode is umask-sensitive; make the durable mode explicit
        # before the first payload readback.
        os.fchmod(child, mode)
        fsync_fd(child)
        offset = 0
        while offset < len(data):
            offset += os.write(child, data[offset:])
        fsync_fd(child)
        before = os.fstat(child)
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or stat.S_IMODE(before.st_mode) != mode or before.st_size != len(data):
            fail("TSSI_STAGE_WRITE", name)
        os.lseek(child, 0, os.SEEK_SET)
        readback = b""
        while len(readback) < len(data):
            chunk = os.read(child, len(data) - len(readback))
            if not chunk:
                break
            readback += chunk
        after = os.fstat(child)
        if readback != data or identity(after) != identity(before) or after.st_nlink != 1 or after.st_size != len(data):
            fail("TSSI_STAGE_WRITE", f"readback:{name}")
        result = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "size": len(data),
            "mode": mode,
            "device": before.st_dev,
            "inode": before.st_ino,
        }
        fsync_dir(fd)
        return result
    finally:
        os.close(child)


def read_at(fd: int, name: str, code: str = "TSSI_RECOVERY") -> bytes:
    child = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
    try:
        st = os.fstat(child)
        if not stat.S_ISREG(st.st_mode):
            fail(code, f"nonregular:{name}")
        data = b""
        while True:
            chunk = os.read(child, 1024 * 1024)
            if not chunk:
                break
            data += chunk
        after = os.fstat(child)
        if (
            identity(st) != identity(after)
            or st.st_size != len(data)
            or st.st_nlink != 1
            or after.st_nlink != 1
        ):
            fail(code, f"race:{name}")
        return data
    except OSError as exc:
        fail(code, f"{name}:{exc}")
    finally:
        os.close(child)


def write_json_at(fd: int, name: str, obj: Any) -> None:
    data = (json.dumps(obj, sort_keys=True, indent=2) + "\n").encode()
    tmp = f".{name}.tmp"
    write_at(fd, tmp, data, 0o600)
    os.replace(tmp, name, src_dir_fd=fd, dst_dir_fd=fd)
    fsync_dir(fd)


def read_json_at(fd: int, name: str) -> Manifest:
    try:
        value = json.loads(read_at(fd, name).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
        fail("TSSI_JOURNAL_MALFORMED", f"TSSI_RECOVERY:manifest:{exc}")
    if not isinstance(value, dict):
        fail("TSSI_JOURNAL_MALFORMED", "TSSI_RECOVERY:manifest-object")
    return cast(Manifest, value)


def mkdir_at(fd: int, name: str) -> int:
    os.mkdir(name, 0o700, dir_fd=fd)
    fsync_dir(fd)
    return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)


def open_journal(handles: TargetHandles, name: str, *, create: bool = False) -> tuple[int, int, int, int]:
    """Open a transaction and its published/partial directory descriptors.

    ``predeclared`` journals intentionally contain no stage or backup
    directory.  A negative descriptor therefore means that the corresponding
    construction has not started; callers must create it through ``mkdir_at``
    and re-open it by descriptor before writing.
    """
    if create:
        os.mkdir(name, 0o700, dir_fd=handles.codex_fd)
        fsync_dir(handles.codex_fd)
    journal_fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=handles.codex_fd)
    backup_fd = stage_fd = restore_fd = -1
    try:
        if create:
            # Restore staging is private journal state and may be created at
            # transaction birth.  Published/partial closures are created only
            # after their owning manifest transition is durable.
            restore_fd = mkdir_at(journal_fd, RESTORE_DIR)
        else:
            for dirname, slot in (("backup", "backup"), ("stage", "stage"), (RESTORE_DIR, "restore")):
                try:
                    child = os.open(
                        dirname,
                        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                        dir_fd=journal_fd,
                    )
                except FileNotFoundError:
                    child = -1
                if slot == "backup":
                    backup_fd = child
                elif slot == "stage":
                    stage_fd = child
                else:
                    restore_fd = child
    except OSError:
        if restore_fd >= 0:
            os.close(restore_fd)
        if stage_fd >= 0:
            os.close(stage_fd)
        if backup_fd >= 0:
            os.close(backup_fd)
        os.close(journal_fd)
        raise
    return journal_fd, backup_fd, stage_fd, restore_fd


def remove_journal(handles: TargetHandles, name: str) -> None:
    journal_fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=handles.codex_fd)
    tomb_name = name if name.endswith(CLEANUP_SUFFIX) else name + CLEANUP_SUFFIX
    try:
        entries = set(safe_names(journal_fd))
        allowed = {
            "manifest.json",
            ".manifest.json.tmp",
            "stage",
            "stage.partial",
            "backup",
            "backup.partial",
            RESTORE_DIR,
            "rollback-required",
            "committed",
            "cleanup.pending",
        }
        if entries - allowed:
            fail("TSSI_JOURNAL_MALFORMED", "TSSI_RECOVERY:journal-entry")
        manifest_data = read_at(journal_fd, "manifest.json")
        try:
            manifest = cast(Manifest, json.loads(manifest_data.decode("utf-8")))
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
            fail("TSSI_JOURNAL_MALFORMED", f"TSSI_RECOVERY:manifest:{exc}")
        preserved = manifest.get("state")
        if preserved not in {"predeclared", "ready", "backup_constructing", "rolled_back", "committed"}:
            fail("TSSI_JOURNAL_MALFORMED", f"TSSI_RECOVERY:cleanup-state:{preserved}")
        txid = manifest.get("transaction_id")
        if not isinstance(txid, str):
            fail("TSSI_JOURNAL_MALFORMED", "TSSI_RECOVERY:cleanup-owner")
        known_dirs = ("backup", "stage", "backup.partial", "stage.partial", RESTORE_DIR)
        delete_set: list[str] = []
        for dirname in known_dirs:
            if dirname not in entries:
                continue
            child_fd = os.open(dirname, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=journal_fd)
            try:
                delete_set.extend(f"{dirname}/{child}" for child in safe_names(child_fd))
            finally:
                os.close(child_fd)
            delete_set.append(dirname)
        delete_set.extend(entry for entry in (".manifest.json.tmp", "rollback-required", "committed") if entry in entries)
        delete_set = sorted(set(delete_set))
        manifest_digest = hashlib.sha256(manifest_data).hexdigest()
        tomb: dict[str, Any] = {
            "schema_version": 1,
            "transaction_id": txid,
            "manifest_sha256": manifest_digest,
            "preserved_state": preserved,
            "action": "cleanup",
            "delete_set": delete_set,
            "deleted": [],
        }
        if "cleanup.pending" in entries:
            try:
                existing = json.loads(read_at(journal_fd, "cleanup.pending").decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
                fail("TSSI_JOURNAL_MALFORMED", f"TSSI_RECOVERY:tomb:{exc}")
            validate_cleanup_tomb(existing, manifest_data, name)
            tomb = cast(dict[str, Any], existing)
        else:
            write_json_at(journal_fd, "cleanup.pending", tomb)
            fsync_dir(journal_fd)
        if name != tomb_name:
            os.replace(name, tomb_name, src_dir_fd=handles.codex_fd, dst_dir_fd=handles.codex_fd)
            fsync_dir(handles.codex_fd)
        deleted = set(cast(list[str], tomb["deleted"]))
        for relative in sorted(cast(list[str], tomb["delete_set"]), key=lambda value: (-value.count("/"), value)):
            if relative in deleted:
                continue
            parent_name, _, child_name = relative.rpartition("/")
            parent_fd = journal_fd
            close_parent = False
            if parent_name:
                parent_fd = os.open(parent_name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=journal_fd)
                close_parent = True
            try:
                try:
                    if relative in known_dirs:
                        os.rmdir(child_name, dir_fd=parent_fd)
                    else:
                        os.unlink(child_name, dir_fd=parent_fd)
                except FileNotFoundError:
                    pass
            finally:
                if close_parent:
                    os.close(parent_fd)
            deleted.add(relative)
            tomb["deleted"] = sorted(deleted)
            write_json_at(journal_fd, "cleanup.pending", tomb)
            fsync_dir(journal_fd)
        os.unlink("cleanup.pending", dir_fd=journal_fd)
        fsync_dir(journal_fd)
        try:
            os.unlink("manifest.json", dir_fd=journal_fd)
        except FileNotFoundError:
            fail("TSSI_JOURNAL_MALFORMED", "TSSI_RECOVERY:manifestless-tomb")
        fsync_dir(journal_fd)
    finally:
        os.close(journal_fd)
    os.rmdir(tomb_name, dir_fd=handles.codex_fd)
    fsync_dir(handles.codex_fd)


def target_entry(handles: TargetHandles, rel: str) -> TargetEntry:
    parent, name = parent_for(handles, rel)
    try:
        os.stat(name, dir_fd=parent, follow_symlinks=False)
    except FileNotFoundError:
        return TargetEntry(None, None, None, None)
    snap = read_regular(parent, name, rel, bundle=False)
    return TargetEntry(snap.data, snap.mode, snap.device, snap.inode)


def assert_target_entry(handles: TargetHandles, rel: str, expected: TargetEntry) -> None:
    revalidate_target_handles(handles)
    actual = target_entry(handles, rel)
    if actual != expected:
        fail("TSSI_TARGET_RACE", rel)


def chmod_at(fd: int, name: str, mode: int) -> None:
    child = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
    try:
        os.fchmod(child, mode)
        fsync_fd(child)
        if stat.S_IMODE(os.fstat(child).st_mode) != mode:
            fail("TSSI_APPLY_WRITE", f"mode:{name}")
    finally:
        os.close(child)


def validate_manifest(
    manifest: Manifest,
    journal_fd: int,
    stage_fd: int,
    backup_fd: int,
    state: str,
    *,
    allow_terminal_cleanup: bool = False,
    allow_cleanup_tomb: bool = False,
) -> tuple[list[str], dict[str, Any], dict[str, Any]]:
    def malformed(detail: str) -> NoReturn:
        # Keep the legacy recovery marker in the detail for older callers while
        # exposing the normative journal finding to new callers.
        fail("TSSI_JOURNAL_MALFORMED", f"TSSI_RECOVERY:{detail}")

    required = {
        "schema_version", "transaction_id", "source_commit", "bundle_sha256",
        "old", "new", "plan", "state", "expected_stage", "expected_backup",
    }
    if set(manifest) != required or type(manifest.get("schema_version")) is not int or manifest.get("schema_version") != 1:
        malformed("manifest-fields")
    if state not in STATE_CLOSURE_RULES:
        malformed(f"unknown:{state}")
    journal_entries = set(safe_names(journal_fd))
    terminal_cleanup = allow_terminal_cleanup and state in {
        "predeclared", "ready", "backup_constructing", "rolled_back", "committed",
    } and journal_entries in ({"manifest.json"}, {"manifest.json", RESTORE_DIR})
    if allow_terminal_cleanup and not terminal_cleanup:
        malformed("terminal-cleanup-closure")
    if allow_cleanup_tomb and "cleanup.pending" not in journal_entries:
        malformed("cleanup-tomb-anchor")
    transaction_id = manifest.get("transaction_id")
    if not isinstance(transaction_id, str) or not re.fullmatch(r"static-seed-[0-9a-f]{32}", transaction_id):
        malformed("transaction-id")
    source_commit = manifest.get("source_commit")
    bundle_digest = manifest.get("bundle_sha256")
    if not isinstance(source_commit, str) or not COMMIT.fullmatch(source_commit):
        malformed("source-commit")
    if not isinstance(bundle_digest, str) or not DIGEST.fullmatch(bundle_digest):
        malformed("bundle-sha256")
    old_value, new_value = manifest.get("old"), manifest.get("new")
    if not isinstance(old_value, dict) or not isinstance(new_value, dict):
        malformed("old-new-type")
    old = cast(dict[str, Any], old_value)
    new = cast(dict[str, Any], new_value)
    paths = sorted(old.keys())
    if not paths or paths != sorted(set(paths)) or set(new) != set(paths):
        malformed("old-new-path-closure")
    for path in paths:
        if path not in {PROVENANCE, CONFIG} and not re.fullmatch(r"\.codex/agents/[A-Za-z0-9_-]+\.toml", path):
            malformed(f"path:{path}")
        for mapping, label in ((old, "old"), (new, "new")):
            raw_item = mapping[path]
            if not isinstance(raw_item, dict):
                malformed(f"{label}-entry:{path}")
            item = cast(dict[str, Any], raw_item)
            if set(item) != {"exists", "sha256", "size", "mode", "device", "inode", "type"}:
                malformed(f"{label}-entry:{path}")
            exists = item["exists"]
            if type(exists) is not bool:
                malformed(f"{label}-exists:{path}")
            if not exists:
                if any(item[key] is not None for key in ("sha256", "size", "mode", "device", "inode")) or item["type"] != "absent":
                    malformed(f"{label}-absent:{path}")
                continue
            if not isinstance(item["sha256"], str) or not DIGEST.fullmatch(item["sha256"]):
                malformed(f"{label}-digest:{path}")
            if type(item["size"]) is not int or item["size"] < 0 or item["mode"] != 0o644 or item["type"] != "regular":
                malformed(f"{label}-value:{path}")
            if label == "old" and (type(item["device"]) is not int or type(item["inode"]) is not int or item["device"] <= 0 or item["inode"] <= 0):
                malformed(f"old-identity:{path}")
            if label == "new":
                if state in {"predeclared", "ready", "backup_constructing", "backed_up"}:
                    if item["device"] is not None or item["inode"] is not None:
                        malformed(f"new-identity-early:{path}")
                elif type(item["device"]) is not int or type(item["inode"]) is not int or item["device"] <= 0 or item["inode"] <= 0:
                    malformed(f"new-identity:{path}")
    plan_value = manifest.get("plan")
    if not isinstance(plan_value, dict) or set(cast(dict[str, Any], plan_value).keys()) != {"added", "updated", "deleted", "write_order"}:
        malformed("plan-fields")
    plan_obj = cast(dict[str, Any], plan_value)
    sets: dict[str, list[str]] = {}
    for key in ("added", "updated", "deleted", "write_order"):
        raw_value = plan_obj[key]
        if not isinstance(raw_value, list):
            malformed(f"plan-{key}")
        value = cast(list[Any], raw_value)
        if any(not isinstance(p, str) for p in value) or value != sorted(set(cast(list[str], value))):
            malformed(f"plan-{key}")
        sets[key] = cast(list[str], value)
        if not set(value).issubset(set(paths)):
            malformed(f"plan-closure:{key}")
    if set(sets["added"]) & set(sets["updated"]) or set(sets["added"]) & set(sets["deleted"]) or set(sets["updated"]) & set(sets["deleted"]):
        malformed("plan-overlap")
    expected_added = {p for p in paths if not old[p]["exists"] and new[p]["exists"]}
    expected_deleted = {p for p in paths if old[p]["exists"] and not new[p]["exists"]}
    expected_updated = {p for p in paths if old[p]["exists"] and new[p]["exists"] and (old[p]["sha256"], old[p]["mode"]) != (new[p]["sha256"], new[p]["mode"])}
    if set(sets["added"]) != expected_added or set(sets["deleted"]) != expected_deleted or set(sets["updated"]) != expected_updated:
        malformed("plan-mapping")
    expected_order = sorted(expected_added | expected_updated | expected_deleted)
    if sets["write_order"] != expected_order:
        malformed("plan-order")
    for key in ("expected_stage", "expected_backup"):
        value = manifest.get(key)
        if not isinstance(value, dict) or set(cast(dict[str, Any], value).keys()) != {"paths", "digests", "tree_sha256", "marker", "published"}:
            malformed(f"{key}-fields")
        item = cast(dict[str, Any], value)
        raw_paths = item["paths"]
        if not isinstance(raw_paths, list):
            malformed(f"{key}-paths")
        path_values = cast(list[Any], raw_paths)
        if any(not isinstance(p, str) for p in path_values):
            malformed(f"{key}-paths")
        path_strings = cast(list[str], path_values)
        if path_strings != sorted(set(path_strings)):
            malformed(f"{key}-paths")
        raw_digests = item["digests"]
        if not isinstance(raw_digests, dict):
            malformed(f"{key}-digests")
        digest_values = cast(dict[str, Any], raw_digests)
        if set(digest_values) != set(path_strings):
            malformed(f"{key}-digests")
        if any(not isinstance(d, str) or not DIGEST.fullmatch(d) for d in digest_values.values()):
            malformed(f"{key}-digest")
        if item["tree_sha256"] is not None and (not isinstance(item["tree_sha256"], str) or not DIGEST.fullmatch(item["tree_sha256"])):
            malformed(f"{key}-tree")
        if item["published"] and item["tree_sha256"] is None:
            malformed(f"{key}-published-tree")
        if not item["published"] and item["tree_sha256"] is not None:
            malformed(f"{key}-partial-tree")
        if item["marker"] != "COMPLETE" or type(item["published"]) is not bool:
            malformed(f"{key}-values")
    expected_stage = {f"{paths.index(p):04d}.blob" for p in sets["write_order"] if new[p]["exists"]}
    expected_backup = {f"{index:04d}.blob" for index, p in enumerate(paths) if old[p]["exists"]}
    if set(manifest["expected_stage"]["paths"]) != expected_stage or set(manifest["expected_backup"]["paths"]) != expected_backup:
        malformed("expected-closure")
    expected_stage_digests = {name: new[paths[int(name[:4])]]["sha256"] for name in expected_stage}
    expected_backup_digests = {name: old[paths[int(name[:4])]]["sha256"] for name in expected_backup}
    if cast(dict[str, Any], manifest["expected_stage"])["digests"] != expected_stage_digests or cast(dict[str, Any], manifest["expected_backup"])["digests"] != expected_backup_digests:
        malformed("expected-digest-mapping")
    stage_published = bool(cast(dict[str, Any], manifest["expected_stage"])["published"])
    backup_published = bool(cast(dict[str, Any], manifest["expected_backup"])["published"])
    markers = journal_entries
    stage_publication_promotion = (
        not allow_cleanup_tomb
        and state == "predeclared"
        and not stage_published
        and stage_fd >= 0
        and backup_fd < 0
        and not ({"rollback-required", "committed"} & markers)
    )
    backup_publication_promotion = (
        not allow_cleanup_tomb
        and state == "backup_constructing"
        and stage_published
        and stage_fd >= 0
        and not backup_published
        and backup_fd >= 0
        and "rollback-required" in markers
        and "committed" not in markers
    )
    if stage_publication_promotion:
        try:
            verify_marker(journal_fd, stage_fd, "COMPLETE", "stage", transaction_id, manifest, "stage")
        except ImportError_ as exc:
            malformed(f"stage-publication:{exc.detail}")
    if backup_publication_promotion:
        try:
            verify_marker(journal_fd, backup_fd, "COMPLETE", "backup", transaction_id, manifest, "backup")
        except ImportError_ as exc:
            malformed(f"backup-publication:{exc.detail}")
    if not terminal_cleanup and not allow_cleanup_tomb and not stage_publication_promotion and stage_published != (stage_fd >= 0):
        malformed("stage-publication-closure")
    if not terminal_cleanup and not allow_cleanup_tomb and not backup_publication_promotion and backup_published != (backup_fd >= 0):
        malformed("backup-publication-closure")
    if stage_published and cast(dict[str, Any], manifest["expected_stage"])["tree_sha256"] != closure_tree_digest(cast(dict[str, Any], manifest["expected_stage"])):
        malformed("stage-tree-mapping")
    if backup_published and cast(dict[str, Any], manifest["expected_backup"])["tree_sha256"] != closure_tree_digest(cast(dict[str, Any], manifest["expected_backup"])):
        malformed("backup-tree-mapping")
    cleanup_mode = terminal_cleanup or allow_cleanup_tomb or "cleanup.pending" in markers or (
        state in {"committed", "rolled_back"} and markers <= {"manifest.json", RESTORE_DIR}
    )
    # The only published-closure crash exceptions are the two explicitly
    # represented by the durable state table.
    if state == "predeclared" and backup_published:
        malformed("predeclared-backup-published")
    if state == "ready" and not stage_published:
        malformed("ready-stage-unpublished")
    if state in {"backup_constructing", "backed_up", "applied", "read_back", "rolled_back", "rollback_failed", "committed"} and not stage_published:
        malformed(f"{state}-stage-unpublished")
    if not cleanup_mode and state in {"backed_up", "applied", "read_back", "rolled_back", "rollback_failed", "committed"} and (not backup_published or "rollback-required" not in markers):
        malformed(f"{state}-backup-closure")
    if not cleanup_mode and state == "backup_constructing" and not backup_publication_promotion and backup_published != ("rollback-required" in markers):
        malformed("backup-constructing-publication")
    if state == "predeclared" and stage_published and "rollback-required" in markers:
        malformed("predeclared-marker")
    if set(safe_names(journal_fd)) - {"manifest.json", ".manifest.json.tmp", "backup", "stage", "backup.partial", "stage.partial", RESTORE_DIR, "rollback-required", "committed", "cleanup.pending"}:
        malformed("journal-closure")
    return paths, old, new


def verify_expected_blob(fd: int, name: str, manifest: Manifest, prefix: str) -> bytes:
    digest, size, mode = expected_blob_meta(manifest, prefix, name)
    try:
        st = os.stat(name, dir_fd=fd, follow_symlinks=False)
    except OSError as exc:
        fail("TSSI_RECOVERY", f"blob-missing:{name}:{exc}")
    if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or stat.S_IMODE(st.st_mode) != mode or st.st_size != size:
        fail("TSSI_RECOVERY", f"blob-shape:{name}")
    data = read_at(fd, name)
    if len(data) != size or hashlib.sha256(data).hexdigest() != digest:
        fail("TSSI_RECOVERY", f"blob-digest:{name}")
    return data


def optional_dir(fd: int, name: str) -> int:
    """Open an owned journal directory, returning -1 only for absence."""
    try:
        return os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
    except FileNotFoundError:
        return -1
    except OSError as exc:
        fail("TSSI_RECOVERY", f"journal-directory:{name}:{exc}")


def ensure_dir(fd: int, name: str) -> int:
    existing = optional_dir(fd, name)
    if existing >= 0:
        return existing
    return mkdir_at(fd, name)


def close_fd(fd: int) -> None:
    if fd >= 0:
        os.close(fd)


def durable_manifest(handles: TargetHandles, journal_fd: int, name: str, manifest: Manifest) -> None:
    write_json_at(journal_fd, "manifest.json", manifest)
    fsync_dir(journal_fd)
    fsync_dir(handles.codex_fd)


def expected_blob_names(manifest: Manifest, prefix: str) -> set[str]:
    expected = cast(dict[str, Any], manifest["expected_stage" if prefix == "stage" else "expected_backup"])
    return set(cast(list[str], expected["paths"]))


def expected_blob_meta(manifest: Manifest, prefix: str, name: str) -> tuple[str, int, int]:
    try:
        index = int(name[:4])
        paths = sorted(cast(dict[str, Any], manifest["old"]))
        path = paths[index]
    except (ValueError, IndexError, KeyError, TypeError):
        fail("TSSI_RECOVERY", f"blob-name:{prefix}:{name}")
    item = cast(dict[str, Any], cast(dict[str, Any], manifest["new" if prefix == "stage" else "old"])[path])
    if not item["exists"]:
        fail("TSSI_RECOVERY", f"blob-missing-entry:{prefix}:{name}")
    expected = cast(dict[str, Any], manifest["expected_stage" if prefix == "stage" else "expected_backup"])
    digest = cast(dict[str, str], expected["digests"]).get(name)
    if digest is None:
        fail("TSSI_RECOVERY", f"blob-missing-meta:{prefix}:{name}")
    return digest, cast(int, item["size"]), cast(int, item["mode"])


def verify_partial_entry(fd: int, name: str, manifest: Manifest, prefix: str) -> None:
    if not re.fullmatch(r"[0-9]{4}\.blob", name):
        fail("TSSI_RECOVERY", f"partial-name:{prefix}:{name}")
    expected, size, mode = expected_blob_meta(manifest, prefix, name)
    try:
        st = os.stat(name, dir_fd=fd, follow_symlinks=False)
    except OSError as exc:
        fail("TSSI_RECOVERY", f"partial-entry:{name}:{exc}")
    if not stat.S_ISREG(st.st_mode) or stat.S_IMODE(st.st_mode) != mode or st.st_nlink != 1 or st.st_size != size:
        fail("TSSI_RECOVERY", f"partial-shape:{name}")
    data = read_at(fd, name)
    if hashlib.sha256(data).hexdigest() != expected:
        fail("TSSI_RECOVERY", f"partial-digest:{name}")


def marker_data(kind: str, transaction_id: str, blobs: dict[str, Any], prefix: str) -> bytes:
    entries: list[dict[str, Any]] = []
    del prefix
    for name in cast(list[str], blobs["paths"]):
        entries.append({
            "name": name,
            "sha256": cast(dict[str, str], blobs["digests"])[name],
        })
    return (json.dumps({"kind": kind, "transaction_id": transaction_id, "entries": entries}, sort_keys=True) + "\n").encode()


def closure_tree_digest(expected: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    digests = cast(dict[str, str], expected["digests"])
    for name in cast(list[str], expected["paths"]):
        digest.update(name.encode() + b"\0" + digests[name].encode() + b"\0")
    return digest.hexdigest()


def write_marker(fd: int, name: str, data: bytes) -> None:
    write_at(fd, name, data, 0o600)
    fsync_dir(fd)


def verify_marker(
    journal_fd: int,
    directory_fd: int,
    marker_name: str,
    kind: str,
    transaction_id: str,
    manifest: Manifest,
    prefix: str,
    *,
    allow_consumed: bool = False,
) -> None:
    if directory_fd < 0:
        fail("TSSI_RECOVERY", f"missing-{kind}-directory")
    try:
        actual = read_marker(directory_fd, "COMPLETE").decode("utf-8")
    except (UnicodeDecodeError, ImportError_) as exc:
        fail("TSSI_RECOVERY", f"{kind}-complete:{exc}")
    expected = marker_data(kind, cast(str, manifest["transaction_id"]), cast(dict[str, Any], manifest["expected_stage" if prefix == "stage" else "expected_backup"]), prefix).decode()
    if actual != expected:
        fail("TSSI_RECOVERY", f"{kind}-complete-mismatch")
    expected_names = expected_blob_names(manifest, prefix)
    names = set(safe_names(directory_fd)) - {"COMPLETE"}
    if (not allow_consumed and names != expected_names) or (allow_consumed and not names.issubset(expected_names)):
        fail("TSSI_RECOVERY", f"{kind}-closure")
    expected_closure = cast(dict[str, Any], manifest["expected_stage" if prefix == "stage" else "expected_backup"])
    if expected_closure["published"] and expected_closure["tree_sha256"] != closure_tree_digest(expected_closure):
        fail("TSSI_RECOVERY", f"{kind}-tree")
    verify_names = names if allow_consumed else expected_names
    for name in sorted(verify_names):
        verify_expected_blob(directory_fd, name, manifest, prefix)


def verify_partial_directory(fd: int, manifest: Manifest, prefix: str) -> None:
    if fd < 0:
        return
    expected_names = expected_blob_names(manifest, prefix)
    names = set(safe_names(fd))
    for name in names:
        if name == "COMPLETE":
            # A marker in a partial directory is valid only if it is handled
            # as a publication boundary; never silently treat it as partial.
            fail("TSSI_RECOVERY", f"partial-marker:{prefix}")
        if name not in expected_names:
            fail("TSSI_RECOVERY", f"partial-closure:{prefix}:{name}")
        verify_partial_entry(fd, name, manifest, prefix)


def verify_construction_directory(
    journal_fd: int,
    fd: int,
    manifest: Manifest,
    prefix: str,
    transaction_id: str,
) -> None:
    """Validate a partial closure, including the crash window after COMPLETE."""
    if fd < 0:
        return
    if "COMPLETE" in set(safe_names(fd)):
        verify_marker(journal_fd, fd, "COMPLETE", prefix, transaction_id, manifest, prefix)
    else:
        verify_partial_directory(fd, manifest, prefix)


STATE_CLOSURE_RULES: dict[str, dict[str, set[str]]] = {
    "predeclared": {
        "required_dirs": set(),
        "forbidden_dirs": {"backup", "backup.partial"},
        "forbidden_markers": {"rollback-required", "committed"},
    },
    "ready": {
        "required_dirs": {"stage"},
        "forbidden_dirs": {"stage.partial", "backup.partial", "backup"},
        "forbidden_markers": {"rollback-required", "committed"},
    },
    "backup_constructing": {
        "required_dirs": {"stage"},
        "forbidden_dirs": {"stage.partial"},
        "forbidden_markers": {"committed"},
    },
    "backed_up": {
        "required_dirs": {"backup"},
        "forbidden_dirs": {"backup.partial", "stage.partial"},
        "required_markers": {"rollback-required"},
        "forbidden_markers": {"committed"},
    },
    "applied": {
        "required_dirs": {"stage", "backup"},
        "forbidden_dirs": {"backup.partial", "stage.partial"},
        "required_markers": {"rollback-required"},
    },
    "read_back": {
        "required_dirs": {"stage", "backup"},
        "forbidden_dirs": {"backup.partial", "stage.partial"},
        "required_markers": {"rollback-required"},
        "forbidden_markers": set(),
    },
    "rolled_back": {
        "required_dirs": {"stage", "backup"},
        "forbidden_dirs": set(),
        "forbidden_markers": {"committed"},
        "required_markers": {"rollback-required"},
    },
    "committed": {
        "required_dirs": {"stage", "backup"},
        "forbidden_dirs": set(),
        "required_markers": {"rollback-required", "committed"},
    },
    "rollback_failed": {
        "required_dirs": {"stage", "backup"},
        "forbidden_dirs": set(),
        "required_markers": {"rollback-required"},
        "forbidden_markers": {"committed"},
    },
}


def validate_cleanup_tomb(value: Any, manifest_data: bytes, journal_name: str) -> None:
    if not isinstance(value, dict) or set(cast(dict[str, Any], value).keys()) != {
        "schema_version", "transaction_id", "manifest_sha256", "preserved_state",
        "action", "delete_set", "deleted",
    }:
        fail("TSSI_JOURNAL_MALFORMED", "TSSI_RECOVERY:tomb-fields")
    tomb = cast(dict[str, Any], value)
    if type(tomb["schema_version"]) is not int or tomb["schema_version"] != 1:
        fail("TSSI_JOURNAL_MALFORMED", "TSSI_RECOVERY:tomb-schema")
    expected_txid = transaction_id_from_journal_name(journal_name)
    if tomb["transaction_id"] != f"static-seed-{expected_txid}":
        fail("TSSI_JOURNAL_MALFORMED", "TSSI_RECOVERY:tomb-owner")
    if tomb["manifest_sha256"] != hashlib.sha256(manifest_data).hexdigest():
        fail("TSSI_JOURNAL_MALFORMED", "TSSI_RECOVERY:tomb-manifest-digest")
    if tomb["preserved_state"] not in {"predeclared", "ready", "backup_constructing", "rolled_back", "committed"}:
        fail("TSSI_JOURNAL_MALFORMED", "TSSI_RECOVERY:tomb-state")
    if tomb["action"] != "cleanup":
        fail("TSSI_JOURNAL_MALFORMED", "TSSI_RECOVERY:tomb-action")
    known = {"stage", "stage.partial", "backup", "backup.partial", RESTORE_DIR, "rollback-required", "committed", ".manifest.json.tmp"}
    for key in ("delete_set", "deleted"):
        raw_values = tomb[key]
        if not isinstance(raw_values, list):
            fail("TSSI_JOURNAL_MALFORMED", f"TSSI_RECOVERY:tomb-{key}")
        values = cast(list[Any], raw_values)
        if any(not isinstance(item, str) for item in values) or values != sorted(set(cast(list[str], values))):
            fail("TSSI_JOURNAL_MALFORMED", f"TSSI_RECOVERY:tomb-{key}")
        for raw_item in values:
            item = cast(str, raw_item)
            parent = item.split("/", 1)[0]
            if parent not in known or item in {"manifest.json", "cleanup.pending"}:
                fail("TSSI_JOURNAL_MALFORMED", f"TSSI_RECOVERY:tomb-path:{item}")
            if item in {"stage", "backup", "stage.partial", "backup.partial", RESTORE_DIR}:
                continue
            leaf = item.rsplit("/", 1)[-1]
            if parent in {"stage", "backup", "stage.partial", "backup.partial", RESTORE_DIR} and leaf not in {"COMPLETE"} and not re.fullmatch(r"[0-9]{4}\.blob", leaf):
                fail("TSSI_JOURNAL_MALFORMED", f"TSSI_RECOVERY:tomb-path:{item}")
    if not set(cast(list[str], tomb["deleted"])).issubset(set(cast(list[str], tomb["delete_set"]))):
        fail("TSSI_JOURNAL_MALFORMED", "TSSI_RECOVERY:tomb-subset")


def validate_cleanup_progress(journal_fd: int, tomb: dict[str, Any]) -> None:
    """Prove that the tomb's durable deletion cursor matches journal entries."""
    def malformed(detail: str) -> NoReturn:
        fail("TSSI_JOURNAL_MALFORMED", f"TSSI_RECOVERY:cleanup-progress:{detail}")

    entries = set(safe_names(journal_fd))
    allowed = {
        "manifest.json", "cleanup.pending", ".manifest.json.tmp",
        "stage", "stage.partial", "backup", "backup.partial", RESTORE_DIR,
        "rollback-required", "committed",
    }
    if entries - allowed:
        malformed("journal-entry")
    delete_set = set(cast(list[str], tomb["delete_set"]))
    deleted = set(cast(list[str], tomb["deleted"]))
    known_dirs = {"stage", "stage.partial", "backup", "backup.partial", RESTORE_DIR}
    known_files = {".manifest.json.tmp", "rollback-required", "committed"}
    actual_paths: set[str] = set()
    for name in sorted(known_dirs | known_files):
        present = name in entries
        if name not in delete_set:
            if present:
                malformed(f"unlisted:{name}")
            continue
        if not present:
            continue
        actual_paths.add(name)
        if name in known_files:
            continue
        try:
            child_fd = os.open(
                name,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                dir_fd=journal_fd,
            )
        except OSError as exc:
            malformed(f"directory:{name}:{exc}")
        try:
            actual_children = set(safe_names(child_fd))
        finally:
            os.close(child_fd)
        for child in actual_children:
            path = f"{name}/{child}"
            if path not in delete_set:
                malformed(f"unlisted:{path}")
            actual_paths.add(path)
    if deleted & actual_paths:
        malformed("deleted-present")
    reconciled_deleted = deleted | (delete_set - actual_paths)
    if reconciled_deleted != deleted:
        tomb["deleted"] = sorted(reconciled_deleted)
        write_json_at(journal_fd, "cleanup.pending", tomb)
        fsync_dir(journal_fd)


def validate_state_closure(
    state: str,
    journal_entries: set[str],
    stage_fd: int,
    backup_fd: int,
    stage_partial_fd: int,
    backup_partial_fd: int,
) -> None:
    """Reject impossible state/directory/marker cross-products centrally."""
    def malformed(detail: str) -> NoReturn:
        fail("TSSI_JOURNAL_MALFORMED", f"TSSI_RECOVERY:{detail}")

    rule = STATE_CLOSURE_RULES.get(state)
    if rule is None:
        malformed(f"unknown:{state}")
    dirs = {name for name, fd in (
        ("stage", stage_fd),
        ("backup", backup_fd),
        ("stage.partial", stage_partial_fd),
        ("backup.partial", backup_partial_fd),
    ) if fd >= 0}
    missing_dirs = rule.get("required_dirs", set()) - dirs
    if missing_dirs:
        malformed(f"state-{state}-missing-dir:{','.join(sorted(missing_dirs))}")
    forbidden_dirs = rule.get("forbidden_dirs", set()) & dirs
    if forbidden_dirs:
        malformed(f"state-{state}-dir-closure:{','.join(sorted(forbidden_dirs))}")
    required_markers = rule.get("required_markers", set()) - journal_entries
    if required_markers:
        malformed(f"state-{state}-missing-marker:{','.join(sorted(required_markers))}")
    forbidden_markers = rule.get("forbidden_markers", set()) & journal_entries
    if forbidden_markers:
        malformed(f"state-{state}-marker-closure:{','.join(sorted(forbidden_markers))}")
    if "stage" in dirs and "stage.partial" in dirs:
        malformed("stage-cross-product")
    if "backup" in dirs and "backup.partial" in dirs:
        malformed("backup-cross-product")
    if state == "backup_constructing" and ("backup" in dirs) != ("rollback-required" in journal_entries):
        malformed("backup-publication-marker-cross-product")
    if state == "predeclared" and "stage" in dirs and "backup.partial" in dirs:
        malformed("predeclared-stage-backup-cross-product")
    if state in {"backed_up", "applied", "read_back", "rolled_back", "rollback_failed"} and "committed" in journal_entries:
        malformed("backed-up-committed-cross-product")


def state_matches(current: dict[str, TargetEntry], values: dict[str, Any], paths: list[str]) -> bool:
    if set(values) != set(paths):
        return False
    expected_paths = {path for path in paths if values[path]["exists"]}
    if set(current) != expected_paths:
        return False
    for path in paths:
        item = values[path]
        actual = current.get(path, TargetEntry(None, None, None, None))
        if not item["exists"]:
            if actual.data is not None:
                return False
        elif (
            actual.data is None
            or actual.mode != item["mode"]
            or hashlib.sha256(actual.data).hexdigest() != item["sha256"]
        ):
            return False
    return True


def restore_from_backups(
    handles: TargetHandles,
    backup_fd: int,
    restore_fd: int,
    old: dict[str, Any],
    manifest: Manifest,
    paths: list[str],
) -> None:
    if backup_fd < 0:
        fail("TSSI_RECOVERY", "backup-directory")
    # Verify the complete closure before the first live mutation.  A corrupt
    # or hard-linked backup must never leave a half-restored target.
    for index, rel in enumerate(paths):
        item = old[rel]
        if item["exists"]:
            if f"{index:04d}.blob" not in expected_blob_names(manifest, "backup"):
                fail("TSSI_RECOVERY", f"backup-missing:{rel}")
            verify_expected_blob(backup_fd, f"{index:04d}.blob", manifest, "backup")
    if restore_fd < 0:
        fail("TSSI_RECOVERY", "restore-directory")
    for name in safe_names(restore_fd):
        os.unlink(name, dir_fd=restore_fd)
    fsync_dir(restore_fd)
    for index, rel in reversed(list(enumerate(paths))):
        parent, name = parent_for(handles, rel)
        revalidate_target_handles(handles)
        current = target_entry(handles, rel)
        item = old[rel]
        if item["exists"]:
            backup_name = f"{index:04d}.blob"
            data = verify_expected_blob(backup_fd, backup_name, manifest, "backup")
            temp_name = f"{index:04d}.blob"
            write_at(restore_fd, temp_name, data, 0o644)
            assert_target_entry(handles, rel, current)
            os.replace(temp_name, name, src_dir_fd=restore_fd, dst_dir_fd=parent)
            chmod_at(parent, name, item["mode"])
        elif current.data is not None:
            os.unlink(name, dir_fd=parent)
        fsync_dir(parent)
    fsync_dir(handles.root_fd)
    fsync_dir(handles.codex_fd)
    fsync_dir(handles.agents_fd)


def recover(handles: TargetHandles, bundle: ValidatedBundle) -> str | None:
    names = journal_names(handles)
    if len(names) > 1:
        fail("TSSI_RECOVERY", "multiple")
    if not names:
        return None
    name = names[0]
    journal_fd = backup_fd = stage_fd = restore_fd = -1
    backup_partial_fd = stage_partial_fd = -1
    try:
        journal_fd, backup_fd, stage_fd, restore_fd = open_journal(handles, name)
        journal_entries = set(safe_names(journal_fd))
        if name.endswith(CLEANUP_SUFFIX) and "manifest.json" not in journal_entries:
            fail("TSSI_JOURNAL_MALFORMED", "TSSI_RECOVERY:manifestless-tomb")
        if "cleanup.pending" in journal_entries and "manifest.json" not in journal_entries:
            fail("TSSI_JOURNAL_MALFORMED", "TSSI_RECOVERY:manifestless-tomb")
        if name.endswith(CLEANUP_SUFFIX) and "cleanup.pending" not in journal_entries:
            # A crash after tomb removal but before manifest removal leaves a
            # terminal manifest as the only ownership evidence.  It is still
            # cleanup-only; an empty/unknown tomb is never inferred committed.
            terminal = read_json_at(journal_fd, "manifest.json")
            terminal_state = terminal.get("state")
            if terminal_state not in {"predeclared", "ready", "backup_constructing", "rolled_back", "committed"}:
                fail("TSSI_JOURNAL_MALFORMED", "TSSI_RECOVERY:tomb-terminal-state")
            paths, old, new = validate_manifest(
                terminal,
                journal_fd,
                stage_fd,
                backup_fd,
                cast(str, terminal_state),
                allow_terminal_cleanup=True,
            )
            if not state_matches(read_target(handles, bundle), new if terminal_state == "committed" else old, paths):
                fail("TSSI_RECOVERY", "tomb-terminal-readback")
            os.unlink("manifest.json", dir_fd=journal_fd)
            fsync_dir(journal_fd)
            os.rmdir(name, dir_fd=handles.codex_fd)
            fsync_dir(handles.codex_fd)
            return "committed" if terminal_state == "committed" else "rolled_back"
        cleanup_tomb: dict[str, Any] | None = None
        manifest_data = read_at(journal_fd, "manifest.json")
        if "cleanup.pending" in journal_entries:
            try:
                cleanup_value = json.loads(read_at(journal_fd, "cleanup.pending").decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError, TypeError) as exc:
                fail("TSSI_JOURNAL_MALFORMED", f"TSSI_RECOVERY:tomb:{exc}")
            validate_cleanup_tomb(cleanup_value, manifest_data, name)
            cleanup_tomb = cast(dict[str, Any], cleanup_value)
            validate_cleanup_progress(journal_fd, cleanup_tomb)
        manifest = read_json_at(journal_fd, "manifest.json")
        state_value = manifest.get("state")
        if not isinstance(state_value, str):
            fail("TSSI_RECOVERY", "state")
        paths, old, new = validate_manifest(
            manifest,
            journal_fd,
            stage_fd,
            backup_fd,
            state_value,
            allow_cleanup_tomb=cleanup_tomb is not None,
        )
        transaction_id = transaction_id_from_journal_name(name)
        if manifest["transaction_id"] != f"static-seed-{transaction_id}":
            fail("TSSI_RECOVERY", "transaction-owner")
        if manifest["source_commit"] != bundle.source_commit or manifest["bundle_sha256"] != bundle.digest:
            fail("TSSI_RECOVERY", "bundle-mismatch")
        # The manifest is the exact old/new union, so it may additionally
        # contain stale direct role paths that are scheduled for deletion.
        # Bundle-owned fixed paths must all be present; validate_manifest has
        # already rejected every path outside the direct controlled shape.
        if not set(controlled_paths(bundle)).issubset(paths):
            fail("TSSI_RECOVERY", "manifest-controlled-path-closure")
        if cleanup_tomb is not None:
            if cleanup_tomb["preserved_state"] != state_value:
                fail("TSSI_JOURNAL_MALFORMED", "TSSI_RECOVERY:tomb-state-mismatch")
            current = read_target(handles, bundle)
            if state_value == "committed":
                if not state_matches(current, new, paths):
                    fail("TSSI_RECOVERY", "cleanup-candidate-mismatch")
            elif not state_matches(current, old, paths):
                fail("TSSI_RECOVERY", "cleanup-pre-state-mismatch")
            remove_journal(handles, name)
            return "committed" if state_value == "committed" else "rolled_back"
        stage_partial_fd = optional_dir(journal_fd, "stage.partial")
        backup_partial_fd = optional_dir(journal_fd, "backup.partial")
        validate_state_closure(
            state_value,
            set(safe_names(journal_fd)),
            stage_fd,
            backup_fd,
            stage_partial_fd,
            backup_partial_fd,
        )

        # Construction-incomplete journals are cleanup-only.  A published
        # closure is never inferred from a directory's mere existence.
        if state_value == "predeclared":
            journal_entries = set(safe_names(journal_fd))
            if backup_fd >= 0 or "rollback-required" in journal_entries or "committed" in journal_entries:
                fail("TSSI_RECOVERY", "predeclared-backup-publication")
            if stage_fd >= 0:
                verify_marker(journal_fd, stage_fd, "COMPLETE", "stage", transaction_id, manifest, "stage")
                manifest["expected_stage"]["published"] = True
                manifest["expected_stage"]["tree_sha256"] = closure_tree_digest(cast(dict[str, Any], manifest["expected_stage"]))
            if stage_partial_fd >= 0:
                verify_construction_directory(journal_fd, stage_partial_fd, manifest, "stage", transaction_id)
            if backup_partial_fd >= 0:
                verify_construction_directory(journal_fd, backup_partial_fd, manifest, "backup", transaction_id)
            current = read_target(handles, bundle)
            if not state_matches(current, old, paths):
                fail("TSSI_RECOVERY", "pre-live-change")
            if stage_fd >= 0:
                manifest["state"] = "ready"
                durable_manifest(handles, journal_fd, name, manifest)
                remove_journal(handles, name)
                return "cleaned_ready"
            remove_journal(handles, name)
            return "cleaned_predeclared"

        if state_value == "ready":
            if stage_fd < 0:
                fail("TSSI_RECOVERY", "ready-stage-missing")
            verify_marker(journal_fd, stage_fd, "COMPLETE", "stage", transaction_id, manifest, "stage")
            if stage_partial_fd >= 0 or backup_partial_fd >= 0 or backup_fd >= 0:
                fail("TSSI_RECOVERY", "ready-closure")
            current = read_target(handles, bundle)
            if not state_matches(current, old, paths):
                fail("TSSI_RECOVERY", "pre-live-change")
            remove_journal(handles, name)
            return "cleaned_ready"

        if state_value == "backup_constructing":
            if stage_fd < 0:
                fail("TSSI_RECOVERY", "backup-stage-missing")
            verify_marker(journal_fd, stage_fd, "COMPLETE", "stage", transaction_id, manifest, "stage")
            if backup_partial_fd >= 0:
                verify_construction_directory(journal_fd, backup_partial_fd, manifest, "backup", transaction_id)
            marker_names = set(safe_names(journal_fd))
            if backup_fd >= 0:
                if "rollback-required" not in marker_names:
                    fail("TSSI_RECOVERY", "backup-marker-missing")
                verify_marker(journal_fd, backup_fd, "COMPLETE", "backup", transaction_id, manifest, "backup")
                verify_rollback_marker(journal_fd, manifest)
                manifest["expected_backup"]["published"] = True
                manifest["expected_backup"]["tree_sha256"] = closure_tree_digest(cast(dict[str, Any], manifest["expected_backup"]))
                manifest["state"] = "backed_up"
                durable_manifest(handles, journal_fd, name, manifest)
                state_value = "backed_up"
            else:
                current = read_target(handles, bundle)
                if not state_matches(current, old, paths):
                    fail("TSSI_RECOVERY", "pre-live-change")
                remove_journal(handles, name)
                return "cleaned_backup_constructing"

        if state_value in {"backed_up", "applied", "read_back"}:
            if stage_fd < 0:
                fail("TSSI_RECOVERY", "stage-missing")
            verify_marker(journal_fd, stage_fd, "COMPLETE", "stage", transaction_id, manifest, "stage", allow_consumed=True)
            if backup_fd < 0:
                fail("TSSI_RECOVERY", "backup-missing")
            if "rollback-required" not in set(safe_names(journal_fd)):
                fail("TSSI_RECOVERY", "rollback-marker-missing")
            verify_marker(journal_fd, backup_fd, "COMPLETE", "backup", transaction_id, manifest, "backup")
            verify_rollback_marker(journal_fd, manifest)
            if state_value == "applied" and "committed" in set(safe_names(journal_fd)):
                current = read_target(handles, bundle)
                if state_matches(current, new, paths):
                    manifest["state"] = "committed"
                    durable_manifest(handles, journal_fd, name, manifest)
                    state_value = "committed"
                else:
                    state_value = "applied"
            if state_value in {"backed_up", "applied", "read_back"}:
                if restore_fd < 0:
                    restore_fd = ensure_dir(journal_fd, RESTORE_DIR)
                restore_from_backups(handles, backup_fd, restore_fd, old, manifest, paths)
                current = read_target(handles, bundle)
                if not state_matches(current, old, paths):
                    fail("TSSI_RECOVERY", "rollback-readback")
                manifest["state"] = "rolled_back"
                durable_manifest(handles, journal_fd, name, manifest)
                remove_journal(handles, name)
                return "rolled_back"

        if state_value == "rollback_failed":
            fail("TSSI_RECOVERY", "rollback_failed")

        if state_value == "rolled_back":
            current = read_target(handles, bundle)
            if not state_matches(current, old, paths):
                fail("TSSI_RECOVERY", "rolled-back-mismatch")
            remove_journal(handles, name)
            return "rolled_back"

        if state_value == "committed":
            if "committed" not in set(safe_names(journal_fd)):
                fail("TSSI_RECOVERY", "committed-marker-missing")
            verify_committed_marker(journal_fd, manifest)
            current = read_target(handles, bundle)
            if not state_matches(current, new, paths):
                if backup_fd < 0 or "rollback-required" not in set(safe_names(journal_fd)):
                    fail("TSSI_RECOVERY", "committed-candidate-mismatch")
                verify_marker(journal_fd, backup_fd, "COMPLETE", "backup", transaction_id, manifest, "backup")
                verify_rollback_marker(journal_fd, manifest)
                if restore_fd < 0:
                    restore_fd = ensure_dir(journal_fd, RESTORE_DIR)
                restore_from_backups(handles, backup_fd, restore_fd, old, manifest, paths)
                if not state_matches(read_target(handles, bundle), old, paths):
                    fail("TSSI_RECOVERY", "rollback-readback")
                manifest["state"] = "rolled_back"
                durable_manifest(handles, journal_fd, name, manifest)
                remove_journal(handles, name)
                return "rolled_back"
            try:
                remove_journal(handles, name)
            except Exception:
                return "committed_cleanup"
            return "committed"
        fail("TSSI_RECOVERY", f"unknown:{state_value}")
    except ImportError_:
        raise
    except Exception as exc:
        fail("TSSI_RECOVERY", f"{exc}")
    finally:
        for fd in (backup_partial_fd, stage_partial_fd, restore_fd, stage_fd, backup_fd, journal_fd):
            if fd >= 0:
                os.close(fd)


def committed_marker_data(manifest: Manifest) -> bytes:
    payload = {
        "kind": "committed",
        "transaction_id": manifest["transaction_id"],
        "source_commit": manifest["source_commit"],
        "bundle_sha256": manifest["bundle_sha256"],
    }
    return (json.dumps(payload, sort_keys=True) + "\n").encode()


def rollback_marker_data(manifest: Manifest) -> bytes:
    payload = {
        "kind": "rollback-required",
        "transaction_id": manifest["transaction_id"],
        "source_commit": manifest["source_commit"],
        "bundle_sha256": manifest["bundle_sha256"],
    }
    return (json.dumps(payload, sort_keys=True) + "\n").encode()


def read_marker(fd: int, name: str) -> bytes:
    try:
        st = os.stat(name, dir_fd=fd, follow_symlinks=False)
    except OSError as exc:
        fail("TSSI_RECOVERY", f"marker:{name}:{exc}")
    if not stat.S_ISREG(st.st_mode) or stat.S_IMODE(st.st_mode) != 0o600 or st.st_nlink != 1:
        fail("TSSI_RECOVERY", f"marker-shape:{name}")
    return read_at(fd, name)


def verify_rollback_marker(journal_fd: int, manifest: Manifest) -> None:
    if read_marker(journal_fd, "rollback-required") != rollback_marker_data(manifest):
        fail("TSSI_RECOVERY", "rollback-marker")


def verify_committed_marker(journal_fd: int, manifest: Manifest) -> None:
    if read_marker(journal_fd, "committed") != committed_marker_data(manifest):
        fail("TSSI_RECOVERY", "committed-marker")


def perform_import(root: Path, bundle: ValidatedBundle, rootfd: int, bundlefd: int) -> tuple[str, dict[str, int]]:
    del root
    handles = target_lock(rootfd)
    journal_fd = backup_fd = stage_fd = restore_fd = -1
    backup_partial_fd = stage_partial_fd = -1
    try:
        recovery = recover(handles, bundle)
        if recovery is not None:
            return recovery, {"roles": len(bundle.roles), "added": 0, "updated": 0, "deleted": 0}
        revalidate_bundle(bundlefd, bundle)
        current = read_target(handles, bundle)
        missing = TargetEntry(None, None, None, None)
        desired = {PROVENANCE: bundle.provenance, CONFIG: bundle.config}
        desired.update({f"{ROLE_DIR}/{name}.toml": data for name, data in bundle.roles.items()})
        all_paths = sorted(set(current) | set(desired))
        added = sum(current.get(p, missing).data is None and p in desired for p in all_paths)
        deleted = sum(current.get(p, missing).data is not None and p not in desired for p in all_paths)
        updated = sum(
            current.get(p, missing).data is not None
            and p in desired
            and current.get(p, missing).data != desired[p]
            for p in all_paths
        )
        plan = [
            p
            for p in all_paths
            if (p not in desired) != (current.get(p, missing).data is None)
            or (p in desired and current.get(p, missing).data != desired[p])
        ]
        if not plan:
            return "noop", {"roles": len(bundle.roles), "added": 0, "updated": 0, "deleted": 0}
        revalidate_bundle(bundlefd, bundle)
        current_again = read_target(handles, bundle)
        if any(current_again.get(path, missing) != current.get(path, missing) for path in all_paths):
            fail("TSSI_TARGET_RACE", "pre-journal")

        transaction_id = secrets.token_hex(16)
        journal_name = f"{JOURNAL_PREFIX}{transaction_id}{JOURNAL_SUFFIX}"
        journal_fd, backup_fd, stage_fd, restore_fd = open_journal(handles, journal_name, create=True)
        old_manifest: dict[str, Any] = {}
        new_manifest: dict[str, Any] = {}
        for path in all_paths:
            item = current.get(path, missing)
            old_manifest[path] = {
                "exists": item.data is not None,
                "sha256": hashlib.sha256(item.data).hexdigest() if item.data is not None else None,
                "size": len(item.data) if item.data is not None else None,
                "mode": item.mode,
                "device": item.device,
                "inode": item.inode,
                "type": "regular" if item.data is not None else "absent",
            }
            new_manifest[path] = {
                "exists": path in desired,
                "sha256": hashlib.sha256(desired[path]).hexdigest() if path in desired else None,
                "size": len(desired[path]) if path in desired else None,
                "mode": 0o644 if path in desired else None,
                "device": None,
                "inode": None,
                "type": "regular" if path in desired else "absent",
            }
        added_paths = sorted(p for p in all_paths if not old_manifest[p]["exists"] and new_manifest[p]["exists"])
        deleted_paths = sorted(p for p in all_paths if old_manifest[p]["exists"] and not new_manifest[p]["exists"])
        updated_paths = sorted(p for p in all_paths if old_manifest[p]["exists"] and new_manifest[p]["exists"] and (old_manifest[p]["sha256"], old_manifest[p]["mode"]) != (new_manifest[p]["sha256"], new_manifest[p]["mode"]))
        write_order = sorted(added_paths + updated_paths + deleted_paths)
        stage_paths = [f"{all_paths.index(p):04d}.blob" for p in write_order if new_manifest[p]["exists"]]
        backup_paths = [f"{index:04d}.blob" for index, p in enumerate(all_paths) if old_manifest[p]["exists"]]
        stage_digests = {name: new_manifest[all_paths[int(name[:4])]]["sha256"] for name in stage_paths}
        backup_digests = {name: old_manifest[all_paths[int(name[:4])]]["sha256"] for name in backup_paths}
        tx_manifest_id = f"static-seed-{transaction_id}"
        manifest: Manifest = {
            "schema_version": 1,
            "transaction_id": tx_manifest_id,
            "state": "predeclared",
            "source_commit": bundle.source_commit,
            "bundle_sha256": bundle.digest,
            "old": old_manifest,
            "new": new_manifest,
            "plan": {"added": added_paths, "updated": updated_paths, "deleted": deleted_paths, "write_order": write_order},
            "expected_stage": {"paths": stage_paths, "digests": stage_digests, "tree_sha256": None, "marker": "COMPLETE", "published": False},
            "expected_backup": {"paths": backup_paths, "digests": backup_digests, "tree_sha256": None, "marker": "COMPLETE", "published": False},
        }
        stage_index = {path: index for index, path in enumerate(all_paths) if path in plan and path in desired}
        try:
            # Ownership declaration is the first durable transaction evidence.
            durable_manifest(handles, journal_fd, journal_name, manifest)

            # Stage closure: partial bytes, COMPLETE marker, then one atomic
            # directory publication.  The manifest remains predeclared until
            # the published closure has been fully fsynced.
            stage_partial_fd = mkdir_at(journal_fd, "stage.partial")
            for path in plan:
                if path in desired:
                    blob_name = f"{stage_index[path]:04d}.blob"
                    blob = write_at(stage_partial_fd, blob_name, desired[path], 0o644)
                    if blob["sha256"] != cast(dict[str, str], manifest["expected_stage"]["digests"])[blob_name]:
                        fail("TSSI_STAGE_WRITE", blob_name)
                    durable_manifest(handles, journal_fd, journal_name, manifest)
            write_marker(
                stage_partial_fd,
                "COMPLETE",
                marker_data("stage", cast(str, manifest["transaction_id"]), cast(dict[str, Any], manifest["expected_stage"]), "stage"),
            )
            fsync_dir(stage_partial_fd)
            os.replace("stage.partial", "stage", src_dir_fd=journal_fd, dst_dir_fd=journal_fd)
            fsync_dir(journal_fd)
            stage_fd = os.open("stage", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=journal_fd)
            manifest["expected_stage"]["published"] = True
            manifest["expected_stage"]["tree_sha256"] = closure_tree_digest(cast(dict[str, Any], manifest["expected_stage"]))
            manifest["state"] = "ready"
            durable_manifest(handles, journal_fd, journal_name, manifest)

            # Claim backup construction before creating its partial directory.
            manifest["state"] = "backup_constructing"
            durable_manifest(handles, journal_fd, journal_name, manifest)
            backup_partial_fd = mkdir_at(journal_fd, "backup.partial")
            for index, path in enumerate(all_paths):
                item = current.get(path, missing)
                if item.data is not None:
                    blob_name = f"{index:04d}.blob"
                    blob = write_at(backup_partial_fd, blob_name, item.data, 0o644)
                    if blob["sha256"] != cast(dict[str, str], manifest["expected_backup"]["digests"])[blob_name]:
                        fail("TSSI_STAGE_WRITE", blob_name)
                    durable_manifest(handles, journal_fd, journal_name, manifest)
            write_marker(
                backup_partial_fd,
                "COMPLETE",
                marker_data("backup", cast(str, manifest["transaction_id"]), cast(dict[str, Any], manifest["expected_backup"]), "backup"),
            )
            fsync_dir(backup_partial_fd)
            os.replace("backup.partial", "backup", src_dir_fd=journal_fd, dst_dir_fd=journal_fd)
            fsync_dir(journal_fd)
            backup_fd = os.open("backup", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=journal_fd)
            manifest["expected_backup"]["published"] = True
            manifest["expected_backup"]["tree_sha256"] = closure_tree_digest(cast(dict[str, Any], manifest["expected_backup"]))
            write_marker(journal_fd, "rollback-required", rollback_marker_data(manifest))
            manifest["state"] = "backed_up"
            durable_manifest(handles, journal_fd, journal_name, manifest)

            revalidate_bundle(bundlefd, bundle)
            if read_target(handles, bundle) != current:
                fail("TSSI_TARGET_RACE", "pre-apply")

            for path in plan:
                parent, name = parent_for(handles, path)
                assert_target_entry(handles, path, current.get(path, missing))
                if path in desired:
                    staged_name = f"{stage_index[path]:04d}.blob"
                    verify_expected_blob(stage_fd, staged_name, manifest, "stage")
                    os.replace(staged_name, name, src_dir_fd=stage_fd, dst_dir_fd=parent)
                    chmod_at(parent, name, 0o644)
                else:
                    os.unlink(name, dir_fd=parent)
                fsync_dir(parent)
            fsync_dir(handles.root_fd)
            fsync_dir(handles.codex_fd)
            fsync_dir(handles.agents_fd)
            after = read_target(handles, bundle)
            for path in all_paths:
                if new_manifest[path]["exists"]:
                    new_manifest[path]["device"] = after[path].device
                    new_manifest[path]["inode"] = after[path].inode
            manifest["state"] = "applied"
            durable_manifest(handles, journal_fd, journal_name, manifest)
            if not state_matches(after, new_manifest, all_paths):
                fail("TSSI_READBACK", "candidate")
            manifest["state"] = "read_back"
            durable_manifest(handles, journal_fd, journal_name, manifest)
            write_marker(journal_fd, "committed", committed_marker_data(manifest))
            manifest["state"] = "committed"
            durable_manifest(handles, journal_fd, journal_name, manifest)
            try:
                remove_journal(handles, journal_name)
            except Exception:
                return "committed_cleanup", {"roles": len(bundle.roles), "added": added, "updated": updated, "deleted": deleted}
            return "pass", {"roles": len(bundle.roles), "added": added, "updated": updated, "deleted": deleted}
        except Exception as exc:
            try:
                journal_entries = set(safe_names(journal_fd))
                complete_backup = backup_fd >= 0 and "rollback-required" in journal_entries
                if complete_backup:
                    restore_from_backups(
                        handles,
                        backup_fd,
                        restore_fd,
                        old_manifest,
                        manifest,
                        all_paths,
                    )
                    if not state_matches(read_target(handles, bundle), old_manifest, all_paths):
                        fail("TSSI_ROLLBACK", "readback")
                    manifest["state"] = "rolled_back"
                    durable_manifest(handles, journal_fd, journal_name, manifest)
                else:
                    if not state_matches(read_target(handles, bundle), old_manifest, all_paths):
                        fail("TSSI_ROLLBACK", "pre-state")
                remove_journal(handles, journal_name)
            except Exception as rollback_exc:
                manifest["state"] = "rollback_failed"
                try:
                    durable_manifest(handles, journal_fd, journal_name, manifest)
                except Exception as manifest_exc:
                    raise ImportError_("TSSI_ROLLBACK", f"failed:{rollback_exc};journal:{manifest_exc}") from exc
                raise ImportError_("TSSI_ROLLBACK", f"failed:{rollback_exc}") from exc
            if isinstance(exc, ImportError_):
                raise ImportError_(exc.code, f"{exc.detail};TSSI_ROLLBACK=pass") from exc
            raise ImportError_("TSSI_APPLY_WRITE", f"{exc};TSSI_ROLLBACK=pass") from exc
        finally:
            for fd in (backup_partial_fd, stage_partial_fd, restore_fd, stage_fd, backup_fd, journal_fd):
                close_fd(fd)
    finally:
        try:
            fcntl.flock(handles.agents_fd, fcntl.LOCK_UN)
        finally:
            handles.close()


def result_line(status: str, bundle: ValidatedBundle, counts: dict[str, int], recovery: str | None = None) -> str:
    if status == "committed":
        return f"TEMPLATE_STATIC_SEED_IMPORT=pass recovered=committed source_commit={bundle.source_commit} roles={counts['roles']} added=0 updated=0 deleted=0"
    if status == "pass":
        return f"TEMPLATE_STATIC_SEED_IMPORT=pass source_commit={bundle.source_commit} roles={counts['roles']} added={counts['added']} updated={counts['updated']} deleted={counts['deleted']}"
    if status == "noop":
        return f"TEMPLATE_STATIC_SEED_IMPORT=noop source_commit={bundle.source_commit} roles={counts['roles']} added=0 updated=0 deleted=0"
    return f"TEMPLATE_STATIC_SEED_IMPORT=fail recovery={recovery or status}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True, help="fresh static-seed export directory")
    args = parser.parse_args(argv)
    root = project_root()
    rootfd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
    bundlefd = -1
    try:
        bundlefd = open_lexical_directory(args.bundle)
        bundle = open_bundle_files(bundlefd)
        status, counts = perform_import(root, bundle, rootfd, bundlefd)
        print(result_line(status, bundle, counts, status if status not in {"pass", "noop"} else None))
        return 0 if status in {"pass", "noop", "committed"} else 1
    except ImportError_ as exc:
        print(f"{exc.code}{':' + exc.detail if exc.detail else ''}", file=sys.stderr)
        return 75 if exc.code == "TSSI_CONCURRENT_IMPORT" else (1 if exc.code.startswith(("TSSI_RECOVERY", "TSSI_JOURNAL_MALFORMED")) else 2)
    except OSError as exc:
        print(f"TSSI_TARGET_SHAPE:{exc}", file=sys.stderr)
        return 2
    finally:
        if bundlefd >= 0:
            os.close(bundlefd)
        os.close(rootfd)


if __name__ == "__main__":
    raise SystemExit(main())
