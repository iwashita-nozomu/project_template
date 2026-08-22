#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
test_list="${TEST_LIST_PATH:-$repo_root/test/testlist.toml}"

[[ -f "$test_list" ]] || {
  printf 'TEST_RUNNER_ERROR=missing-test-list path=%s\n' "$test_list" >&2
  exit 2
}

export PROJECT_TEST_REPOSITORY_ROOT="$repo_root"
export PROJECT_TEST_LIST_PATH="$test_list"
export PROJECT_TEST_ENVIRONMENT_OWNER="${PROJECT_TEST_ENVIRONMENT_OWNER:-host-project-environment}"

python3 - <<'PY'
from __future__ import annotations

import os
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path


ROOT = Path(os.environ["PROJECT_TEST_REPOSITORY_ROOT"]).resolve()
TEST_LIST = Path(os.environ["PROJECT_TEST_LIST_PATH"]).resolve()
DECLARED_ENVIRONMENT_OWNER = "invocation-environment"
EXPECTED_RESPONSIBILITY = "parent-repository"
ENVIRONMENT_OWNER = os.environ["PROJECT_TEST_ENVIRONMENT_OWNER"].strip()


def fail(message: str) -> "NoReturn":
    print(f"TEST_RUNNER_ERROR={message}", file=sys.stderr)
    raise SystemExit(2)


def command_text(command: list[str]) -> str:
    return shlex.join(command)


try:
    with TEST_LIST.open("rb") as stream:
        payload = tomllib.load(stream)
except (OSError, tomllib.TOMLDecodeError) as exc:
    fail(f"invalid-test-list path={TEST_LIST} error={exc}")

if payload.get("format") != "parent-test-list-v1":
    fail("unsupported-test-list-format")
if payload.get("environment_owner") != DECLARED_ENVIRONMENT_OWNER:
    fail("test-list-environment-owner-mismatch")
if payload.get("responsibility") != EXPECTED_RESPONSIBILITY:
    fail("test-list-responsibility-mismatch")

tests = payload.get("tests")
if not isinstance(tests, list) or not tests:
    fail("test-list-must-contain-tests")

if not ENVIRONMENT_OWNER:
    fail("execution-environment-owner-missing")

print(f"TEST_RUNNER_ENVIRONMENT_OWNER={ENVIRONMENT_OWNER}")
print(f"TEST_RUNNER_RESPONSIBILITY={EXPECTED_RESPONSIBILITY}")
print(f"TEST_RUNNER_ROOT={ROOT}")
print(f"TEST_RUNNER_LIST={TEST_LIST}")

for index, entry in enumerate(tests, start=1):
    if not isinstance(entry, dict):
        fail(f"test-entry-not-table:index={index}")

    name = entry.get("name")
    command = entry.get("command")
    working_directory = entry.get("working_directory", ".")
    if not isinstance(name, str) or not name:
        fail(f"test-name-invalid:index={index}")
    if (
        not isinstance(command, list)
        or not command
        or any(not isinstance(part, str) or not part for part in command)
    ):
        fail(f"test-command-invalid:name={name}")
    if not isinstance(working_directory, str) or not working_directory:
        fail(f"test-working-directory-invalid:name={name}")

    cwd = (ROOT / working_directory).resolve()
    try:
        cwd.relative_to(ROOT)
    except ValueError:
        fail(f"test-working-directory-outside-repository:name={name}")
    if not cwd.is_dir():
        fail(f"test-working-directory-missing:name={name}:path={cwd}")

    argv = [str(part) for part in command]
    rendered = command_text(argv)
    print(f"TEST_START name={name} command={rendered}", flush=True)
    try:
        result = subprocess.run(argv, cwd=cwd, check=False)
        return_code = result.returncode
    except OSError as exc:
        return_code = 127
        print(f"TEST_COMMAND_ERROR name={name} error={exc}", file=sys.stderr)

    if return_code != 0:
        print(f"TEST_FAILURE_NAME={name}", file=sys.stderr)
        print(f"TEST_FAILURE_COMMAND={rendered}", file=sys.stderr)
        print(
            f"TEST_FAILURE_ENVIRONMENT_OWNER={ENVIRONMENT_OWNER}",
            file=sys.stderr,
        )
        print(
            f"TEST_FAILURE_RESPONSIBILITY={EXPECTED_RESPONSIBILITY}",
            file=sys.stderr,
        )
        print(f"TEST_FAILURE_EXIT_CODE={return_code}", file=sys.stderr)
        raise SystemExit(return_code if return_code > 0 else 1)

    print(f"TEST_PASS name={name}", flush=True)

print(f"TEST_RUNNER_RESULT=pass count={len(tests)}")
PY
