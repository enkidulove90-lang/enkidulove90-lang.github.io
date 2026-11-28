"""notion_sync overwrite-not-skip: retire a page's stale post file on slug change."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from notion_sync import retire_stale_post  # noqa: E402


class RetireStalePostTest(unittest.TestCase):
    def setUp(self):
        self.posts = Path(tempfile.mkdtemp())

    def _make(self, name: str) -> Path:
        p = self.posts / name
        p.write_text("# post", encoding="utf-8")
        return p

    def test_same_filename_is_kept(self):
        self._make("paper-a.md")
        state = {"pid1@file": "paper-a.md"}
        self.assertEqual(retire_stale_post(state, "pid1", "paper-a.md", self.posts), "")

    def test_changed_slug_removes_old_file(self):
        old = self._make("paper-a-old.md")
        self._make("paper-a-new.md")
        state = {"pid1@file": "paper-a-old.md"}
        removed = retire_stale_post(state, "pid1", "paper-a-new.md", self.posts)
        self.assertEqual(removed, "paper-a-old.md")
        self.assertFalse(old.exists(), "stale duplicate must be removed")

    def test_missing_old_file_noop(self):
        state = {"pid1@file": "paper-a-old.md"}
        self.assertEqual(retire_stale_post(state, "pid1", "paper-a-new.md", self.posts), "")

    def test_no_previous_record_noop(self):
        self.assertEqual(retire_stale_post({}, "pid1", "paper-a.md", self.posts), "")


if __name__ == "__main__":
    unittest.main()
