# @dependency-start
# responsibility Tests test audit and fix links behavior.
# upstream implementation ../../tools/docs/audit_and_fix_links.py link audit helper under test
# upstream design ../../documents/TROUBLESHOOTING.md documentation maintenance guidance
# @dependency-end
"""Tests for the markdown link audit helper."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "tools" / "docs" / "audit_and_fix_links.py"


class AuditAndFixLinksTest(unittest.TestCase):
    """Exercise the link audit helper through its CLI."""

    def run_cli(self, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        """Run the link audit helper and capture its output."""
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )

    def write_file(self, path: Path, contents: str) -> None:
        """Create a file with parent directories as needed."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")

    def test_check_fails_on_unresolved_links(self) -> None:
        """Check mode should fail when a link cannot be resolved."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self.write_file(
                root / "documents" / "guide.md",
                "# Guide\n\n[missing](./missing.md)\n",
            )

            result = self.run_cli(root, "--check", "documents")

            self.assertEqual(result.returncode, 1)
            self.assertIn("unresolved: 1", result.stdout)
            report = (root / "reports" / "broken_links.txt").read_text(encoding="utf-8")
            self.assertIn("missing.md", report)

    def test_apply_rewrites_uniquely_resolvable_relative_targets(self) -> None:
        """Apply mode should rewrite uniquely resolvable local targets."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            self.write_file(root / "README.md", "# Root\n")
            self.write_file(
                root / "agents" / "guide.md",
                "# Guide\n\n[root](README.md)\n",
            )

            apply_result = self.run_cli(root, "--apply", "agents")
            self.assertEqual(apply_result.returncode, 0, apply_result.stderr)

            rewritten = (root / "agents" / "guide.md").read_text(encoding="utf-8")
            self.assertIn("[root](../README.md)", rewritten)

            check_result = self.run_cli(root, "--check", "agents")
            self.assertEqual(check_result.returncode, 0, check_result.stdout)
            self.assertIn("unresolved: 0", check_result.stdout)

    def test_workspace_absolute_links_become_pending_relative_fixes(self) -> None:
        """Workspace absolute links should be rewritten to portable relative links."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            absolute_readme = f"/tmp/workspace/{root.name}/README.md"
            self.write_file(root / "README.md", "# Root\n")
            self.write_file(
                root / "agents" / "guide.md",
                f"# Guide\n\n[root]({absolute_readme})\n",
            )

            check_result = self.run_cli(root, "--check", "agents")
            self.assertEqual(check_result.returncode, 1, check_result.stdout)
            self.assertIn("pending_fixes: 1", check_result.stdout)

            apply_result = self.run_cli(root, "--apply", "agents")
            self.assertEqual(apply_result.returncode, 0, apply_result.stderr)

            rewritten = (root / "agents" / "guide.md").read_text(encoding="utf-8")
            self.assertIn("[root](../README.md)", rewritten)


if __name__ == "__main__":
    unittest.main()
