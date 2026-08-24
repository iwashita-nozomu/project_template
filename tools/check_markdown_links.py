#!/usr/bin/env python3
"""Check local links in the reader-facing template documentation."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)")


def fail(message: str) -> None:
    """Emit one documentation finding and stop."""
    print(f"DOCS_FINDING={message}", file=sys.stderr)
    raise SystemExit(1)


tracked = subprocess.run(
    [
        "git",
        "-C",
        str(ROOT),
        "ls-files",
        "--cached",
        "--others",
        "--exclude-standard",
        "--",
        "*.md",
    ],
    check=True,
    capture_output=True,
    text=True,
).stdout.splitlines()

for relative in tracked:
    document = ROOT / relative
    if not document.is_file():
        continue
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
