#!/usr/bin/env python3
"""Perform focused static checks for repository-owned GitHub workflows."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github/workflows"
DESIGN = ROOT / "documents/design/github-actions.md"
FORBIDDEN = (
    "vendor/agent-canon",
    "tools/agent-canon",
    "AGENT_CANON_",
    "agent_canon_source_root",
    "checkout_agent_canon_submodule",
    "submodules: recursive",
)


def fail(message: str) -> None:
    """Emit one workflow finding and stop."""
    print(f"WORKFLOW_FINDING={message}", file=sys.stderr)
    raise SystemExit(1)


files = sorted([*WORKFLOWS.glob("*.yml"), *WORKFLOWS.glob("*.yaml")])
if not files:
    fail("no-workflows")
for path in files:
    text = path.read_text(encoding="utf-8")
    for required in ("name:", "on:", "jobs:"):
        if required not in text:
            fail(f"missing-key:{path.name}:{required}")
    for token in FORBIDDEN:
        if token in text:
            fail(f"forbidden-runtime-reference:{path.name}:{token}")

ci = (WORKFLOWS / "ci.yml").read_text(encoding="utf-8")
for required_name in ("name: Repository CI", "name: Fresh Clone Acceptance"):
    if required_name not in ci:
        fail(f"required-check-name-missing:{required_name}")
if "make fresh-clone-check" not in ci:
    fail("canonical-command-missing")
for command in (
    "bash docker/run-tests.sh --tag project-template:ci",
):
    if command not in ci:
        fail(f"project-container-command-missing:{command}")

if not DESIGN.is_file():
    fail("github-actions-design-missing")
design = DESIGN.read_text(encoding="utf-8")
for path in files:
    relative = path.relative_to(ROOT).as_posix()
    if f"`{relative}`" not in design:
        fail(f"github-actions-design-workflow-missing:{relative}")
for required in (
    "Repository CI",
    "Fresh Clone Acceptance",
    "dynamic/github-code-scanning/codeql",
    "dynamic/dependabot/update-graph",
    "dynamic/copilot-swe-agent/copilot",
):
    if required not in design:
        fail(f"github-actions-design-contract-missing:{required}")

print("GITHUB_WORKFLOW_CHECK=pass")
