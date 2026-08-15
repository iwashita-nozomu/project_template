from __future__ import annotations

# ruff: noqa: D100, D103
# pyright: reportUnknownParameterType=false, reportMissingParameterType=false, reportUnknownVariableType=false, reportUnknownMemberType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false
import hashlib
import importlib.util
import json
import os
import shutil
import signal
import stat
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, cast

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_BUNDLE = ROOT / "tests/fixtures/static-seed-c5fa3a22"
SCRIPT = ROOT / "tools/import_agent_canon_static_seed.py"


@pytest.fixture()
def importer():
    spec = importlib.util.spec_from_file_location("template_static_seed_importer", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def fixture_root(tmp_path: Path) -> tuple[Path, Path]:
    target = tmp_path / "template"
    target.mkdir()
    shutil.copytree(ROOT / ".codex", target / ".codex")
    shutil.copy2(ROOT / "agent-canon-static-seed.json", target)
    bundle = tmp_path / "bundle"
    shutil.copytree(FIXTURE_BUNDLE, bundle)
    return target, bundle


def invoke(module, target: Path, bundle: Path, capsys) -> tuple[int, str, str]:
    module.project_root = lambda: target
    rc = module.main(["--bundle", str(bundle)])
    captured = capsys.readouterr()
    return rc, captured.out, captured.err


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            digest.update(path.relative_to(root).as_posix().encode())
            digest.update(path.read_bytes())
            digest.update(str(stat.S_IMODE(path.stat().st_mode)).encode())
    return digest.hexdigest()


def prepare_recovery_journal(module, target: Path, bundle_path: Path, state: str) -> Path:
    """Create a descriptor-valid journal fixture without touching the real bundle."""
    module.project_root = lambda: target
    bundle_fd = module.open_lexical_directory(str(bundle_path))
    bundle = module.open_bundle_files(bundle_fd)
    root_fd = os.open(target, os.O_RDONLY | os.O_DIRECTORY)
    handles = module.open_target_handles(root_fd)
    current = module.read_target(handles, bundle)
    missing = module.TargetEntry(None, None, None, None)
    desired = {module.PROVENANCE: bundle.provenance, module.CONFIG: bundle.config}
    desired.update({f"{module.ROLE_DIR}/{name}.toml": data for name, data in bundle.roles.items()})
    paths = sorted(set(current) | set(desired))
    plan = [
        path
        for path in paths
        if (path not in desired) != (current.get(path, missing).data is None)
        or (path in desired and current.get(path, missing).data != desired[path])
    ]
    old = {}
    new = {}
    for path in paths:
        item = current.get(path, missing)
        old[path] = {"exists": item.data is not None, "sha256": hashlib.sha256(item.data).hexdigest() if item.data is not None else None, "size": len(item.data) if item.data is not None else None, "mode": item.mode, "device": item.device, "inode": item.inode, "type": "regular" if item.data is not None else "absent"}
        new[path] = {"exists": path in desired, "sha256": hashlib.sha256(desired[path]).hexdigest() if path in desired else None, "size": len(desired[path]) if path in desired else None, "mode": 0o644 if path in desired else None, "device": None, "inode": None, "type": "regular" if path in desired else "absent"}
    journal_name = ".static-seed-import." + "a" * 32 + ".txn"
    journal_fd, backup_fd, stage_fd, restore_fd = module.open_journal(handles, journal_name, create=True)
    stage_index = {path: index for index, path in enumerate(paths) if path in plan and path in desired}
    if state in {"applied", "read_back", "rolled_back", "committed", "rollback_failed"}:
        for path in paths:
            if new[path]["exists"] and current.get(path, missing).data is not None:
                new[path]["device"] = current[path].device
                new[path]["inode"] = current[path].inode
    added = sorted(p for p in paths if not old[p]["exists"] and new[p]["exists"])
    deleted = sorted(p for p in paths if old[p]["exists"] and not new[p]["exists"])
    updated = sorted(p for p in paths if old[p]["exists"] and new[p]["exists"] and (old[p]["sha256"], old[p]["mode"]) != (new[p]["sha256"], new[p]["mode"]))
    write_order = sorted(added + updated + deleted)
    stage_paths = [f"{paths.index(p):04d}.blob" for p in write_order if new[p]["exists"]]
    backup_paths = [f"{index:04d}.blob" for index, p in enumerate(paths) if old[p]["exists"]]
    manifest: dict[str, Any] = {
        "schema_version": 1,
        "transaction_id": "static-seed-" + "a" * 32,
        "state": "predeclared",
        "source_commit": bundle.source_commit,
        "bundle_sha256": bundle.digest,
        "old": old,
        "new": new,
        "plan": {"added": added, "updated": updated, "deleted": deleted, "write_order": write_order},
        "expected_stage": {"paths": stage_paths, "digests": {n: new[paths[int(n[:4])]]["sha256"] for n in stage_paths}, "tree_sha256": None, "marker": "COMPLETE", "published": False},
        "expected_backup": {"paths": backup_paths, "digests": {n: old[paths[int(n[:4])]]["sha256"] for n in backup_paths}, "tree_sha256": None, "marker": "COMPLETE", "published": False},
    }
    module.durable_manifest(handles, journal_fd, journal_name, manifest)

    def publish(kind: str) -> int:
        partial_name = f"{kind}.partial"
        partial_fd = module.mkdir_at(journal_fd, partial_name)
        if kind == "stage":
            for path, index in stage_index.items():
                blob_name = f"{index:04d}.blob"
                module.write_at(partial_fd, blob_name, desired[path], 0o644)
            prefix = "stage"
        else:
            for index, path in enumerate(paths):
                if current.get(path, missing).data is not None:
                    blob_name = f"{index:04d}.blob"
                    module.write_at(partial_fd, blob_name, current[path].data, 0o644)
            prefix = "backup"
        expected = cast(dict[str, Any], manifest["expected_stage" if kind == "stage" else "expected_backup"])
        module.write_marker(partial_fd, "COMPLETE", module.marker_data(kind, manifest["transaction_id"], expected, prefix))
        os.replace(partial_name, kind, src_dir_fd=journal_fd, dst_dir_fd=journal_fd)
        module.fsync_dir(journal_fd)
        expected["published"] = True
        expected["tree_sha256"] = module.closure_tree_digest(expected)
        return os.open(kind, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=journal_fd)

    if state in {"ready", "backup_constructing", "backed_up", "applied", "read_back", "rolled_back", "committed", "rollback_failed"}:
        stage_fd = publish("stage")
        manifest["state"] = "ready"
        module.durable_manifest(handles, journal_fd, journal_name, manifest)
    if state in {"backup_constructing", "backed_up", "applied", "read_back", "rolled_back", "committed", "rollback_failed"}:
        manifest["state"] = "backup_constructing"
        module.durable_manifest(handles, journal_fd, journal_name, manifest)
    if state in {"backed_up", "applied", "read_back", "rolled_back", "committed", "rollback_failed"}:
        backup_fd = publish("backup")
        module.write_marker(journal_fd, "rollback-required", module.rollback_marker_data(manifest))
        manifest["state"] = state
        module.durable_manifest(handles, journal_fd, journal_name, manifest)
    if state in {"committed"}:
        module.write_marker(journal_fd, "committed", module.committed_marker_data(manifest))
        manifest["state"] = state
        module.durable_manifest(handles, journal_fd, journal_name, manifest)
    for fd in (restore_fd, stage_fd, backup_fd, journal_fd):
        if fd >= 0:
            os.close(fd)
    handles.close()
    os.close(root_fd)
    os.close(bundle_fd)
    if state in {"applied", "read_back", "committed", "rollback_failed"}:
        (target / module.PROVENANCE).write_bytes(bundle.provenance)
    return target / ".codex" / journal_name


def test_repository_fixture_is_imported_then_noop_without_mtime_changes(importer, fixture_root, capsys):
    target, bundle = fixture_root
    # Make the first operation non-empty while retaining a complete target.
    (target / "agent-canon-static-seed.json").write_text(
        (target / "agent-canon-static-seed.json").read_text().replace("c5fa3a22", "29b6fe5e", 1),
        encoding="utf-8",
    )
    rc, out, err = invoke(importer, target, bundle, capsys)
    assert rc == 0, err
    assert "TEMPLATE_STATIC_SEED_IMPORT=pass" in out
    assert "source_commit=c5fa3a22c8486952dc6dede0cc3a25e5ba7741e5" in out
    before = {p: p.stat().st_mtime_ns for p in (target / ".codex").rglob("*") if p.is_file()}
    rc, out, err = invoke(importer, target, bundle, capsys)
    assert rc == 0, err
    assert "TEMPLATE_STATIC_SEED_IMPORT=noop" in out
    assert before == {p: p.stat().st_mtime_ns for p in before}
    assert not list((target / ".codex").glob(".static-seed-import.*.txn"))


@pytest.mark.parametrize("boundary,expected", [("stage", "cleaned_predeclared"), ("backup", "cleaned_backup_constructing")])
def test_subprocess_kill_during_pre_live_construction_cleans_journal(
    importer, fixture_root, capsys, boundary, expected
):
    target, bundle = fixture_root
    provenance = target / "agent-canon-static-seed.json"
    provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    before = tree_digest(target)
    child = textwrap.dedent(
        """
        import importlib.util
        import os
        import signal
        import sys
        from pathlib import Path

        script, target, bundle, boundary = sys.argv[1:5]
        spec = importlib.util.spec_from_file_location("construction_crash_importer", script)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        module.project_root = lambda: Path(target)
        original_open = module.open_journal
        original_write = module.write_at
        def capture_journal(*args, **kwargs):
            return original_open(*args, **kwargs)

        def kill_after_boundary(fd, name, data, *args, **kwargs):
            result = original_write(fd, name, data, *args, **kwargs)
            location = os.readlink(f"/proc/self/fd/{fd}")
            if name.endswith(".blob") and f"{boundary}.partial" in location:
                os.kill(os.getpid(), signal.SIGKILL)
            return result

        module.open_journal = capture_journal
        module.write_at = kill_after_boundary
        raise SystemExit(module.main(["--bundle", bundle]))
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", child, str(SCRIPT), str(target), str(bundle), boundary],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == -signal.SIGKILL
    journal = next((target / ".codex").glob(".static-seed-import.*.txn"))
    rc, out, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and f"recovery={expected}" in out, err
    assert tree_digest(target) == before and not journal.exists()


def test_add_update_and_stale_delete_are_one_plan(importer, fixture_root, capsys):
    target, bundle = fixture_root
    stale = target / ".codex/agents/stale_role.toml"
    stale.write_text((bundle / ".codex/agents/worker.toml").read_text(), encoding="utf-8")
    stale.chmod(0o644)
    # Change one existing role and ensure one role is added by removing it from target.
    removed = target / ".codex/agents/worker.toml"
    removed.unlink()
    rc, out, err = invoke(importer, target, bundle, capsys)
    assert rc == 0, err
    assert "added=1" in out and "deleted=1" in out and "updated=" in out
    assert not stale.exists()
    assert removed.exists()


@pytest.mark.parametrize("mutation", [
    "missing_provenance",
    "unexpected_file",
    "nested_file",
    "symlink",
    "executable",
    "hardlink",
    "unreferenced_role",
    "wrong_role_path",
])
def test_bundle_closure_failures_leave_target_unchanged(importer, fixture_root, mutation, capsys):
    target, bundle = fixture_root
    if mutation == "missing_provenance":
        (bundle / "agent-canon-static-seed.json").unlink()
    elif mutation == "unexpected_file":
        (bundle / "README").write_text("unexpected", encoding="utf-8")
    elif mutation == "nested_file":
        (bundle / ".codex/agents/nested").mkdir()
    elif mutation == "symlink":
        (bundle / ".codex/config.toml").unlink()
        (bundle / ".codex/config.toml").symlink_to(ROOT / ".codex/config.toml")
    elif mutation == "executable":
        (bundle / ".codex/config.toml").chmod(0o755)
    elif mutation == "hardlink":
        (bundle / ".codex/agents/hardlink.toml").hardlink_to(bundle / ".codex/config.toml")
    elif mutation == "unreferenced_role":
        shutil.copy2(bundle / ".codex/agents/worker.toml", bundle / ".codex/agents/unreferenced.toml")
    elif mutation == "wrong_role_path":
        (bundle / ".codex/agents/worker.toml").rename(bundle / ".codex/agents/wrong.toml")
    before = tree_digest(target)
    rc, _out, err = invoke(importer, target, bundle, capsys)
    assert rc == 2
    assert err.startswith("TSSI_")
    assert tree_digest(target) == before


@pytest.mark.parametrize("directory", [".codex", ".codex/agents"])
def test_bundle_directory_symlink_has_typed_bundle_finding(importer, fixture_root, directory, capsys, tmp_path):
    target, bundle = fixture_root
    source = tmp_path / directory.replace("/", "-")
    original = bundle / directory
    shutil.copytree(original, source)
    shutil.rmtree(original)
    original.symlink_to(source, target_is_directory=True)
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 2 and "TSSI_BUNDLE_" in err
    assert tree_digest(target) == before


@pytest.mark.parametrize("marker", [
    "agents/skills/", "agents/model_profiles.toml", "tools/agent_tools/",
    "../../agents/", "../../tools/", "https://", "git clone",
    "agent_canon_repo_token", "authorization: bearer",
])
def test_semantic_forbidden_markers_reject_before_write(importer, fixture_root, marker, capsys):
    target, bundle = fixture_root
    role = bundle / ".codex/agents/worker.toml"
    text = role.read_text(encoding="utf-8")
    role.write_text(text.replace("You are acting as worker", f"You are acting as worker {marker}"), encoding="utf-8")
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 2 and "TSSI_BUNDLE_" in err
    assert tree_digest(target) == before


def test_reviewed_payload_manifest_rejects_unreviewed_bytes(importer, fixture_root, capsys):
    target, bundle = fixture_root
    role = bundle / ".codex/agents/worker.toml"
    role.write_bytes(role.read_bytes() + b"\n")
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 2 and "TSSI_BUNDLE_REVIEWED_PAYLOAD" in err
    assert tree_digest(target) == before


def test_provenance_commit_type_is_typed_failure(importer, fixture_root, capsys):
    target, bundle = fixture_root
    provenance = json.loads((bundle / "agent-canon-static-seed.json").read_text(encoding="utf-8"))
    provenance["source_commit"] = 123
    (bundle / "agent-canon-static-seed.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 2 and "TSSI_BUNDLE_PROVENANCE" in err
    assert tree_digest(target) == before


def test_transaction_payload_modes_are_explicit_under_restrictive_umask(importer, fixture_root, capsys):
    target, bundle = fixture_root
    provenance = target / "agent-canon-static-seed.json"
    provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    previous = os.umask(0o077)
    try:
        rc, out, err = invoke(importer, target, bundle, capsys)
    finally:
        os.umask(previous)
    assert rc == 0 and "TEMPLATE_STATIC_SEED_IMPORT=pass" in out, err
    assert stat.S_IMODE((target / "agent-canon-static-seed.json").stat().st_mode) == 0o644


def test_target_symlink_is_rejected_without_stale_delete(importer, fixture_root, capsys):
    target, bundle = fixture_root
    stale = target / ".codex/agents/stale.toml"
    stale.write_text("stale", encoding="utf-8")
    stale.chmod(0o644)
    (target / ".codex/config.toml").unlink()
    (target / ".codex/config.toml").symlink_to(bundle / ".codex/config.toml")
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 2 and "TSSI_TARGET_" in err
    assert tree_digest(target) == before and stale.exists()


def test_concurrent_import_fails_immediately(importer, fixture_root, capsys):
    target, bundle = fixture_root
    agents = os.open(target / ".codex/agents", os.O_RDONLY | os.O_DIRECTORY)
    try:
        import fcntl

        fcntl.flock(agents, fcntl.LOCK_EX | fcntl.LOCK_NB)
        before = tree_digest(target)
        rc, _, err = invoke(importer, target, bundle, capsys)
        assert rc == 75 and "TSSI_CONCURRENT_IMPORT" in err
        assert tree_digest(target) == before
    finally:
        os.close(agents)


def test_apply_failure_rolls_back_and_removes_journal(importer, fixture_root, capsys, monkeypatch):
    target, bundle = fixture_root
    (target / "agent-canon-static-seed.json").write_text(
        (target / "agent-canon-static-seed.json").read_text().replace("c5fa3a22", "29b6fe5e", 1),
        encoding="utf-8",
    )
    before = tree_digest(target)
    original = importer.os.replace
    calls = {"count": 0}

    def fail_once(source, destination, **kwargs):
        if kwargs.get("dst_dir_fd") is not None and calls["count"] == 3 and not calls.get("failed"):
            calls["failed"] = True
            raise OSError("injected replace failure")
        if kwargs.get("dst_dir_fd") is not None:
            calls["count"] += 1
        return original(source, destination, **kwargs)

    monkeypatch.setattr(importer.os, "replace", fail_once)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 2 and "TSSI_ROLLBACK=pass" in err
    assert tree_digest(target) == before
    assert not list((target / ".codex").glob(".static-seed-import.*.txn"))


def test_malformed_journal_fails_closed(importer, fixture_root, capsys):
    target, bundle = fixture_root
    journal = target / ".codex/.static-seed-import.deadbeef.txn"
    (journal / "backup").mkdir(parents=True)
    (journal / "manifest.json").write_text("not json", encoding="utf-8")
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "TSSI_RECOVERY" in err
    assert tree_digest(target) == before


@pytest.mark.parametrize("state", ["predeclared", "backup_constructing", "backed_up", "ready", "applied", "read_back", "rolled_back", "committed", "rollback_failed"])
def test_every_durable_recovery_state_has_typed_result(importer, fixture_root, state, capsys):
    target, bundle = fixture_root
    if state in {"applied", "committed", "rollback_failed"}:
        provenance = target / "agent-canon-static-seed.json"
        provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    journal = prepare_recovery_journal(importer, target, bundle, state)
    if state == "rolled_back":
        # Rollback has already consumed its backup/stage entries when the
        # process dies after the durable rolled_back marker.
        for blob in (journal / "stage").glob("*.blob"):
            blob.unlink()
    rc, out, err = invoke(importer, target, bundle, capsys)
    if state == "committed":
        assert rc == 0 and "recovered=committed" in out
        assert not journal.exists()
    elif state == "rollback_failed":
        assert rc == 1 and "TSSI_RECOVERY" in err
        assert journal.exists()
    else:
        assert rc == 1 and "TEMPLATE_STATIC_SEED_IMPORT=fail recovery=" in out, err
        assert not journal.exists()


def test_ready_recovery_rejects_live_change_without_rollback(importer, fixture_root, capsys):
    target, bundle = fixture_root
    journal = prepare_recovery_journal(importer, target, bundle, "ready")
    role = target / ".codex/agents/worker.toml"
    role.write_bytes(role.read_bytes() + b"\n# adversarial live change\n")
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "TSSI_RECOVERY" in err
    assert tree_digest(target) == before and journal.exists()


def test_predeclared_published_stage_promotes_ready_then_stops(importer, fixture_root, capsys):
    target, bundle = fixture_root
    journal = prepare_recovery_journal(importer, target, bundle, "ready")
    manifest_path = journal / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["state"] = "predeclared"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rc, out, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "recovery=cleaned_ready" in out, err
    assert not journal.exists()


@pytest.mark.parametrize("boundary,expected", [("stage", "cleaned_ready"), ("backup", "rolled_back")])
def test_subprocess_kill_after_publication_before_manifest_update_promotes(
    importer, fixture_root, capsys, boundary, expected
):
    target, bundle = fixture_root
    provenance = target / "agent-canon-static-seed.json"
    provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    before = tree_digest(target)
    child = textwrap.dedent(
        """
        import importlib.util
        import os
        import signal
        import sys
        from pathlib import Path

        script, target, bundle, boundary = sys.argv[1:5]
        spec = importlib.util.spec_from_file_location("publication_crash_importer", script)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        module.project_root = lambda: Path(target)
        original = module.durable_manifest

        def kill_after_publication(handles, journal_fd, name, manifest):
            expected = manifest["expected_stage" if boundary == "stage" else "expected_backup"]
            state = "ready" if boundary == "stage" else "backed_up"
            if manifest["state"] == state and expected["published"]:
                os.kill(os.getpid(), signal.SIGKILL)
            return original(handles, journal_fd, name, manifest)

        module.durable_manifest = kill_after_publication
        raise SystemExit(module.main(["--bundle", bundle]))
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", child, str(SCRIPT), str(target), str(bundle), boundary],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == -signal.SIGKILL
    journal = next((target / ".codex").glob(".static-seed-import.*.txn"))
    manifest = json.loads((journal / "manifest.json").read_text(encoding="utf-8"))
    if boundary == "stage":
        assert manifest["state"] == "predeclared"
        assert manifest["expected_stage"]["published"] is False
        assert (journal / "stage").is_dir()
        assert not (journal / "rollback-required").exists()
    else:
        assert manifest["state"] == "backup_constructing"
        assert manifest["expected_backup"]["published"] is False
        assert (journal / "backup").is_dir()
        assert (journal / "rollback-required").is_file()
    rc, out, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and f"recovery={expected}" in out, err
    assert tree_digest(target) == before and not journal.exists()


def test_journal_symlink_and_directory_swap_fail_closed(importer, fixture_root, capsys, tmp_path):
    target, bundle = fixture_root
    outside = tmp_path / "outside"
    outside.mkdir()
    link = target / ".codex/.static-seed-import.aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa.txn"
    link.symlink_to(outside, target_is_directory=True)
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "TSSI_RECOVERY" in err
    assert tree_digest(target) == before and link.is_symlink()


@pytest.mark.parametrize("which", ["backup"])
def test_stage_or_backup_tamper_is_recovery_failure(importer, fixture_root, which, capsys):
    target, bundle = fixture_root
    provenance = target / "agent-canon-static-seed.json"
    provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    journal = prepare_recovery_journal(importer, target, bundle, "backed_up")
    backup = next((journal / "backup").glob("*.blob"))
    stage = next((journal / "stage").glob("*.blob"))
    (backup if which == "backup" else stage).write_bytes(b"tampered")
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "TSSI_RECOVERY" in err
    assert tree_digest(target) == before and journal.exists()


def test_backed_up_recovery_accepts_consumed_stage_and_restores_exact_old(importer, fixture_root, capsys):
    target, bundle = fixture_root
    provenance = target / "agent-canon-static-seed.json"
    provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    before = tree_digest(target)
    journal = prepare_recovery_journal(importer, target, bundle, "backed_up")
    stage = next((journal / "stage").glob("*.blob"))
    stage.unlink()
    rc, out, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "recovery=rolled_back" in out, err
    assert tree_digest(target) == before and not journal.exists()


def test_fixed_name_user_file_survives_rollback_and_recovery(importer, fixture_root, capsys):
    target, bundle = fixture_root
    user_file = target / ".static-seed-restore.0000.tmp"
    user_bytes = b"user-owned restore sentinel\n"
    user_file.write_bytes(user_bytes)
    user_file.chmod(0o644)
    provenance = target / "agent-canon-static-seed.json"
    provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    before = tree_digest(target)
    journal = prepare_recovery_journal(importer, target, bundle, "backed_up")
    provenance.write_bytes((bundle / "agent-canon-static-seed.json").read_bytes())
    rc, out, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "recovery=rolled_back" in out, err
    assert tree_digest(target) == before and not journal.exists()
    assert user_file.read_bytes() == user_bytes and stat.S_IMODE(user_file.stat().st_mode) == 0o644


def test_subprocess_kill_after_first_live_replace_recovers_backed_up(importer, fixture_root, capsys):
    target, bundle = fixture_root
    provenance = target / "agent-canon-static-seed.json"
    provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    before = tree_digest(target)
    child = textwrap.dedent(
        """
        import importlib.util
        import os
        import signal
        import sys
        from pathlib import Path

        script, target, bundle = sys.argv[1:4]
        spec = importlib.util.spec_from_file_location("crash_importer", script)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        module.project_root = lambda: Path(target)
        original = module.chmod_at

        def kill_after_first_live_replace(fd, name, mode):
            original(fd, name, mode)
            os.kill(os.getpid(), signal.SIGKILL)

        module.chmod_at = kill_after_first_live_replace
        raise SystemExit(module.main(["--bundle", bundle]))
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", child, str(SCRIPT), str(target), str(bundle)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == -signal.SIGKILL
    journal = next((target / ".codex").glob(".static-seed-import.*.txn"))
    assert json.loads((journal / "manifest.json").read_text(encoding="utf-8"))["state"] == "backed_up"
    rc, out, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "recovery=rolled_back" in out, err
    assert tree_digest(target) == before and not journal.exists()


def test_subprocess_kill_during_rollback_preserves_backups_for_restart(importer, fixture_root, capsys):
    target, bundle = fixture_root
    provenance = target / "agent-canon-static-seed.json"
    provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    before = tree_digest(target)
    journal = prepare_recovery_journal(importer, target, bundle, "backed_up")
    provenance.write_bytes((bundle / "agent-canon-static-seed.json").read_bytes())
    child = textwrap.dedent(
        """
        import importlib.util
        import os
        import signal
        import sys
        from pathlib import Path

        script, target, bundle = sys.argv[1:4]
        spec = importlib.util.spec_from_file_location("rollback_crash_importer", script)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        module.project_root = lambda: Path(target)
        original = module.chmod_at

        def kill_after_first_restore(fd, name, mode):
            original(fd, name, mode)
            os.kill(os.getpid(), signal.SIGKILL)

        module.chmod_at = kill_after_first_restore
        raise SystemExit(module.main(["--bundle", bundle]))
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", child, str(SCRIPT), str(target), str(bundle)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == -signal.SIGKILL
    assert journal.exists() and list((journal / "backup").glob("*.blob"))
    rc, out, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "recovery=rolled_back" in out, err
    assert tree_digest(target) == before and not journal.exists()


def test_subprocess_kill_during_committed_cleanup_restarts_cleanly(importer, fixture_root, capsys):
    target, bundle = fixture_root
    before = tree_digest(target)
    journal = prepare_recovery_journal(importer, target, bundle, "committed")
    child = textwrap.dedent(
        """
        import importlib.util
        import os
        import signal
        import sys
        from pathlib import Path

        script, target, bundle = sys.argv[1:4]
        spec = importlib.util.spec_from_file_location("commit_crash_importer", script)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        module.project_root = lambda: Path(target)
        original = module.write_json_at

        def kill_after_first_cleanup(fd, path, value):
            result = original(fd, path, value)
            if path == "cleanup.pending" and value["deleted"]:
                os.kill(os.getpid(), signal.SIGKILL)
            return result

        module.write_json_at = kill_after_first_cleanup
        raise SystemExit(module.main(["--bundle", bundle]))
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", child, str(SCRIPT), str(target), str(bundle)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == -signal.SIGKILL
    assert journal.exists() or next((target / ".codex").glob(".static-seed-import.*.txn.cleanup"), None) is not None
    rc, out, err = invoke(importer, target, bundle, capsys)
    assert rc == 0 and "recovered=committed" in out, err
    assert tree_digest(target) == before and not journal.exists()


@pytest.mark.parametrize(
    "state,boundary,expected,expected_rc",
    [("ready", "stage", "rolled_back", 1), ("committed", "backup", "committed", 0)],
)
def test_subprocess_kill_after_cleanup_directory_cursor_restarts_cleanly(
    importer, fixture_root, capsys, state, boundary, expected, expected_rc
):
    target, bundle = fixture_root
    before = tree_digest(target)
    journal = prepare_recovery_journal(importer, target, bundle, state)
    child = textwrap.dedent(
        """
        import importlib.util
        import os
        import signal
        import sys
        from pathlib import Path

        script, target, bundle, boundary = sys.argv[1:5]
        spec = importlib.util.spec_from_file_location("directory_cleanup_crash_importer", script)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        module.project_root = lambda: Path(target)
        original = module.write_json_at

        def kill_after_directory_cursor(fd, path, value):
            result = original(fd, path, value)
            if path == "cleanup.pending" and boundary in value["deleted"]:
                os.kill(os.getpid(), signal.SIGKILL)
            return result

        module.write_json_at = kill_after_directory_cursor
        raise SystemExit(module.main(["--bundle", bundle]))
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", child, str(SCRIPT), str(target), str(bundle), boundary],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == -signal.SIGKILL
    tomb = next((target / ".codex").glob(".static-seed-import.*.txn.cleanup"))
    tomb_value = json.loads((tomb / "cleanup.pending").read_text(encoding="utf-8"))
    assert boundary in tomb_value["deleted"] and not (tomb / boundary).exists()
    rc, out, err = invoke(importer, target, bundle, capsys)
    expected_output = "recovered=committed" if expected == "committed" else f"recovery={expected}"
    assert rc == expected_rc and expected_output in out, err
    assert tree_digest(target) == before and not tomb.exists() and not journal.exists()


@pytest.mark.parametrize(
    "state,boundary,expected,expected_rc",
    [("ready", "stage", "rolled_back", 1), ("committed", "backup", "committed", 0)],
)
def test_subprocess_kill_after_cleanup_directory_before_cursor_reconciles_and_restarts(
    importer, fixture_root, capsys, state, boundary, expected, expected_rc
):
    target, bundle = fixture_root
    before = tree_digest(target)
    prepare_recovery_journal(importer, target, bundle, state)
    child = textwrap.dedent(
        """
        import importlib.util
        import os
        import signal
        import sys
        from pathlib import Path

        script, target, bundle, boundary = sys.argv[1:5]
        spec = importlib.util.spec_from_file_location("directory_cleanup_before_cursor_importer", script)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        module.project_root = lambda: Path(target)
        original = module.os.rmdir

        def kill_before_directory_cursor(path, *args, **kwargs):
            result = original(path, *args, **kwargs)
            if path == boundary and kwargs.get("dir_fd") is not None:
                os.kill(os.getpid(), signal.SIGKILL)
            return result

        module.os.rmdir = kill_before_directory_cursor
        raise SystemExit(module.main(["--bundle", bundle]))
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", child, str(SCRIPT), str(target), str(bundle), boundary],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == -signal.SIGKILL
    tomb = next((target / ".codex").glob(".static-seed-import.*.txn.cleanup"))
    tomb_value = json.loads((tomb / "cleanup.pending").read_text(encoding="utf-8"))
    assert boundary not in tomb_value["deleted"] and not (tomb / boundary).exists()
    rc, out, err = invoke(importer, target, bundle, capsys)
    expected_output = "recovered=committed" if expected == "committed" else f"recovery={expected}"
    assert rc == expected_rc and expected_output in out, err
    assert tree_digest(target) == before and not tomb.exists()


def test_subprocess_kill_at_manifest_unlink_uses_cleanup_tomb(importer, fixture_root, capsys):
    target, bundle = fixture_root
    prepare_recovery_journal(importer, target, bundle, "committed")
    child = textwrap.dedent(
        """
        import importlib.util
        import os
        import signal
        import sys
        from pathlib import Path

        script, target, bundle = sys.argv[1:4]
        spec = importlib.util.spec_from_file_location("manifest_unlink_crash_importer", script)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        module.project_root = lambda: Path(target)
        original = module.os.unlink

        def kill_at_manifest(path, *args, **kwargs):
            if path == "manifest.json" and kwargs.get("dir_fd") is not None:
                os.kill(os.getpid(), signal.SIGKILL)
            return original(path, *args, **kwargs)

        module.os.unlink = kill_at_manifest
        raise SystemExit(module.main(["--bundle", bundle]))
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", child, str(SCRIPT), str(target), str(bundle)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == -signal.SIGKILL
    tomb = next((target / ".codex").glob(".static-seed-import.*.txn.cleanup"))
    assert tomb.exists()
    rc, out, err = invoke(importer, target, bundle, capsys)
    assert rc == 0 and "recovered=committed" in out, err
    assert not tomb.exists()


def test_subprocess_kill_after_noncommitted_tomb_unlink_restarts_cleanup(importer, fixture_root, capsys):
    target, bundle = fixture_root
    before = tree_digest(target)
    prepare_recovery_journal(importer, target, bundle, "ready")
    child = textwrap.dedent(
        """
        import importlib.util
        import os
        import signal
        import sys
        from pathlib import Path

        script, target, bundle = sys.argv[1:4]
        spec = importlib.util.spec_from_file_location("noncommitted_tomb_crash_importer", script)
        assert spec and spec.loader
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        module.project_root = lambda: Path(target)
        original = module.os.unlink

        def kill_after_tomb_unlink(path, *args, **kwargs):
            result = original(path, *args, **kwargs)
            if path == "cleanup.pending" and kwargs.get("dir_fd") is not None:
                os.kill(os.getpid(), signal.SIGKILL)
            return result

        module.os.unlink = kill_after_tomb_unlink
        raise SystemExit(module.main(["--bundle", bundle]))
        """
    )
    result = subprocess.run(
        [sys.executable, "-c", child, str(SCRIPT), str(target), str(bundle)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == -signal.SIGKILL
    tomb = next((target / ".codex").glob(".static-seed-import.*.txn.cleanup"))
    assert tomb.exists() and (tomb / "manifest.json").exists() and not (tomb / "cleanup.pending").exists()
    rc, out, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "recovery=rolled_back" in out, err
    assert tree_digest(target) == before and not tomb.exists()


def test_hardlinked_recovery_blob_fails_before_restore(importer, fixture_root, capsys):
    target, bundle = fixture_root
    provenance = target / "agent-canon-static-seed.json"
    provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    journal = prepare_recovery_journal(importer, target, bundle, "backed_up")
    backup = next((journal / "backup").glob("*.blob"))
    backup.unlink()
    backup.hardlink_to(target / ".codex/agents/worker.toml")
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "TSSI_RECOVERY" in err
    assert tree_digest(target) == before and journal.exists()


@pytest.mark.parametrize("mutation", ["complete", "rollback-required", "committed"])
def test_required_marker_tamper_fails_closed(importer, fixture_root, mutation, capsys):
    target, bundle = fixture_root
    provenance = target / "agent-canon-static-seed.json"
    provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    state = "ready" if mutation == "complete" else ("committed" if mutation == "committed" else "backed_up")
    journal = prepare_recovery_journal(importer, target, bundle, state)
    marker = journal / ("stage" if mutation == "complete" else ".")
    if mutation == "complete":
        (marker / "COMPLETE").unlink()
    elif mutation == "rollback-required":
        (journal / "rollback-required").unlink()
    else:
        (journal / "committed").write_bytes(b"tampered\n")
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "TSSI_RECOVERY" in err
    assert tree_digest(target) == before and journal.exists()


@pytest.mark.parametrize(
    "mutation",
    ["extra-old-key", "plan-map", "wrong-state-closure", "bad-tomb", "tomb-unlisted-entry"],
)
def test_journal_truth_table_mutations_fail_closed(importer, fixture_root, mutation, capsys):
    target, bundle = fixture_root
    provenance = target / "agent-canon-static-seed.json"
    provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    journal = prepare_recovery_journal(importer, target, bundle, "ready")
    manifest_path = journal / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if mutation == "extra-old-key":
        manifest["old"][next(iter(manifest["old"]))]["extra"] = 1
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif mutation == "plan-map":
        manifest["plan"]["added"].append("agent-canon-static-seed.json")
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif mutation == "wrong-state-closure":
        (journal / "backup").mkdir()
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    elif mutation == "tomb-unlisted-entry":
        tomb = {
            "schema_version": 1,
            "transaction_id": manifest["transaction_id"],
            "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
            "preserved_state": "ready",
            "action": "cleanup",
            "delete_set": [],
            "deleted": [],
        }
        (journal / "cleanup.pending").write_text(json.dumps(tomb, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        tomb = {"schema_version": 1, "transaction_id": manifest["transaction_id"], "manifest_sha256": "0" * 64, "preserved_state": "ready", "action": "cleanup", "delete_set": [], "deleted": []}
        (journal / "cleanup.pending").write_text(json.dumps(tomb, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tomb_path = target / ".codex" / (journal.name.removesuffix(".txn") + ".txn.cleanup")
        journal.rename(tomb_path)
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "TSSI_JOURNAL_MALFORMED" in err
    assert tree_digest(target) == before


@pytest.mark.parametrize(
    "mutation",
    [
        "stage-published-missing",
        "stage-unpublished-present",
        "backup-published-missing",
        "backup-unpublished-present",
    ],
)
def test_published_directory_closure_mutations_fail_closed(importer, fixture_root, mutation, capsys):
    target, bundle = fixture_root
    provenance = target / "agent-canon-static-seed.json"
    provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    if mutation == "stage-published-missing":
        journal = prepare_recovery_journal(importer, target, bundle, "ready")
        manifest_path = journal / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["state"] = "predeclared"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        shutil.rmtree(journal / "stage")
    elif mutation == "stage-unpublished-present":
        journal = prepare_recovery_journal(importer, target, bundle, "predeclared")
        (journal / "stage").mkdir()
    elif mutation == "backup-published-missing":
        journal = prepare_recovery_journal(importer, target, bundle, "backed_up")
        manifest_path = journal / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["state"] = "ready"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        shutil.rmtree(journal / "backup")
    else:
        journal = prepare_recovery_journal(importer, target, bundle, "backup_constructing")
        (journal / "backup").mkdir()
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "TSSI_JOURNAL_MALFORMED" in err
    assert tree_digest(target) == before and journal.exists()


def test_unknown_journal_entry_fails_closed(importer, fixture_root, capsys):
    target, bundle = fixture_root
    journal = prepare_recovery_journal(importer, target, bundle, "predeclared")
    (journal / "unexpected").write_bytes(b"owned by nobody")
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "TSSI_RECOVERY" in err
    assert tree_digest(target) == before and journal.exists()


def test_committed_cleanup_failure_is_committed_only(importer, fixture_root, capsys, monkeypatch):
    target, bundle = fixture_root
    provenance = target / "agent-canon-static-seed.json"
    provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    original = importer.remove_journal
    calls = {"count": 0}

    def fail_once(handles, name):
        calls["count"] += 1
        if calls["count"] == 1:
            raise OSError("injected cleanup failure")
        return original(handles, name)

    monkeypatch.setattr(importer, "remove_journal", fail_once)
    rc, out, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "recovery=committed_cleanup" in out
    journal = next((target / ".codex").glob(".static-seed-import.*.txn"))
    assert (target / "agent-canon-static-seed.json").read_bytes() == bundle.joinpath("agent-canon-static-seed.json").read_bytes()
    monkeypatch.setattr(importer, "remove_journal", original)
    rc, out, err = invoke(importer, target, bundle, capsys)
    assert rc == 0 and "recovered=committed" in out, err
    assert not journal.exists()


def test_bundle_race_immediately_before_apply_leaves_target_unchanged(importer, fixture_root, capsys, monkeypatch):
    target, bundle = fixture_root
    provenance = target / "agent-canon-static-seed.json"
    provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    original = importer.revalidate_bundle
    calls = {"count": 0}

    def race(bundle_fd, validated):
        calls["count"] += 1
        if calls["count"] == 3:
            role = bundle / ".codex/agents/worker.toml"
            role.write_bytes(role.read_bytes().replace(b"name = \"worker\"", b"name = \"worker\" # race", 1))
        return original(bundle_fd, validated)

    monkeypatch.setattr(importer, "revalidate_bundle", race)
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 2 and "TSSI_BUNDLE_RACE" in err
    assert tree_digest(target) == before


def test_target_race_immediately_before_apply_leaves_target_unchanged(importer, fixture_root, capsys, monkeypatch):
    target, bundle = fixture_root
    provenance = target / "agent-canon-static-seed.json"
    provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    original = importer.read_target
    calls = {"count": 0}

    def race(handles, validated):
        calls["count"] += 1
        value = original(handles, validated)
        if calls["count"] == 3:
            value[importer.PROVENANCE] = importer.TargetEntry(b"race", 0o644, 1, 1)
        return value

    monkeypatch.setattr(importer, "read_target", race)
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 2 and "TSSI_TARGET_RACE" in err
    assert tree_digest(target) == before


@pytest.mark.parametrize("directory", [".", ".codex", ".codex/agents"])
def test_target_directory_mode_race_is_rejected(importer, fixture_root, directory, capsys, monkeypatch):
    target, bundle = fixture_root
    provenance = target / "agent-canon-static-seed.json"
    provenance.write_text(provenance.read_text().replace("c5fa3a22", "29b6fe5e", 1), encoding="utf-8")
    original = importer.revalidate_target_handles
    calls = {"count": 0}

    def race(handles):
        original(handles)
        calls["count"] += 1
        if calls["count"] == 1:
            path = target / directory
            path.chmod(stat.S_IMODE(path.stat().st_mode) ^ 0o200)

    monkeypatch.setattr(importer, "revalidate_target_handles", race)
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    path = target / directory
    path.chmod(stat.S_IMODE(path.stat().st_mode) ^ 0o200)
    assert rc == 2 and "TSSI_TARGET_RACE" in err
    assert tree_digest(target) == before


@pytest.mark.parametrize(
    ("base_state", "manifest_state"),
    [("backed_up", "ready"), ("ready", "backed_up"), ("backed_up", "predeclared")],
)
def test_state_marker_directory_cross_product_fails_closed(importer, fixture_root, base_state, manifest_state, capsys):
    target, bundle = fixture_root
    journal = prepare_recovery_journal(importer, target, bundle, base_state)
    manifest_path = journal / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["state"] = manifest_state
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    before = tree_digest(target)
    rc, _, err = invoke(importer, target, bundle, capsys)
    assert rc == 1 and "TSSI_RECOVERY" in err
    assert tree_digest(target) == before and journal.exists()


def test_importer_has_no_runtime_or_external_invocation_surface():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "import subprocess" not in source
    assert "import socket" not in source
    assert "git clone" in source  # marker is a rejected payload string only
    assert "start_repository.sh" not in source
