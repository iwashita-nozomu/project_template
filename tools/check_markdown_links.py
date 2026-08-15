#!/usr/bin/env python3
"""Check local links in the reader-facing template documentation."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
DOCS = (
    ROOT / "README.md",
    ROOT / "QUICK_START.md",
    ROOT / "scripts/README.md",
    ROOT / "docker/README.md",
    ROOT / "documents/README.md",
    ROOT / "documents/contracts/licensing-policy.md",
    ROOT / "documents/contracts/template-bootstrap.md",
    ROOT / "documents/contracts/template-github-remote.md",
    ROOT / "documents/contracts/template-validation.md",
    ROOT / "documents/design/docker-zero-build-environment.md",
)
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")


def fail(message: str) -> None:
    print(f"DOCS_FINDING={message}", file=sys.stderr)
    raise SystemExit(1)


for document in DOCS:
    if not document.is_file():
        fail(f"missing:{document.relative_to(ROOT)}")
    text = document.read_text(encoding="utf-8")
    for raw in LINK.findall(text):
        target = raw.strip().split(" ", 1)[0].strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        path_part = unquote(target.split("#", 1)[0])
        resolved = (document.parent / path_part).resolve()
        try:
            resolved.relative_to(ROOT)
        except ValueError:
            fail(f"outside-repository:{document.relative_to(ROOT)}:{target}")
        if not resolved.exists():
            fail(f"broken-local-link:{document.relative_to(ROOT)}:{target}")

print("DOCS_CHECK=pass")
