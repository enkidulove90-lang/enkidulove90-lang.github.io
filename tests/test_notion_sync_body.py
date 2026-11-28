from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from notion_sync import compose_post, merge_front_matter, split_post


class FrontMatterMergeTest(unittest.TestCase):
    def test_remote_value_wins_but_local_only_keys_survive(self):
        existing = "\n\ntitle: \"旧标题\"\n\ndate: 2026-10-04\n\nmathjax: true\n\nslug: \"paper-x\"\n\n"
        generated = "\n\ntitle: \"新标题\"\n\ndate: \"2026-10-04\"\n\nmathjax: \"\"\n\nslug: \"paper-x\"\n\nvenue_name: \"SIGIR\"\n\n"
        merged = merge_front_matter(existing, generated)
        self.assertIn('title: "新标题"', merged)
        self.assertIn('date: "2026-10-04"', merged)
        # An empty Notion column means "not filled", never "erase the local value".
        self.assertIn("mathjax: true", merged)
        self.assertEqual(merged.count("mathjax"), 1)
        # A key only Notion knows about is appended, not dropped.
        self.assertIn('venue_name: "SIGIR"', merged)

    def test_local_order_and_formatting_are_preserved(self):
        existing = "\n\ntitle: \"T\"\n\ncategories: [推荐系统, 多模态推荐]\n\ntags: [论文速读]\n\n"
        generated = "\n\ntitle: \"T2\"\n\ncategories: []\n\ntags: [论文速读, 统一编码]\n\n"
        merged = merge_front_matter(existing, generated)
        self.assertLess(merged.index("title:"), merged.index("categories:"))
        self.assertIn("categories: [推荐系统, 多模态推荐]", merged)
        self.assertIn("tags: [论文速读, 统一编码]", merged)

    def test_empty_existing_front_matter_falls_back_to_generated(self):
        generated = "\n\ntitle: \"T\"\n\n"
        self.assertEqual(merge_front_matter("", generated), generated)


class ComposePostTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def _existing(self, body="## 我的人工正文\n\n一段话。\n"):
        path = self.root / "paper-x.md"
        path.write_text(
            "---\n\ntitle: \"旧标题\"\n\ndate: 2026-10-04\n\nmathjax: true\n\n---\n\n" + body,
            encoding="utf-8")
        return path

    def _generated(self, body="## 一、Notion 正文\n\n另一段话。\n"):
        return ("---\n\ntitle: \"新标题\"\n\ndate: \"2026-10-04\"\n\n---\n\n" + body)

    def test_existing_post_keeps_its_body(self):
        path = self._existing()
        written = compose_post(self._generated(), str(path))
        front, body = split_post(written)
        self.assertIn("我的人工正文", body)
        self.assertNotIn("Notion 正文", body)
        self.assertIn('title: "新标题"', front)
        self.assertIn("mathjax: true", front)

    def test_new_post_is_materialised_in_full(self):
        path = self.root / "brand-new.md"
        generated = self._generated()
        self.assertEqual(compose_post(generated, str(path)), generated)

    def test_sync_body_flag_restores_full_overwrite(self):
        path = self._existing()
        generated = self._generated()
        self.assertEqual(compose_post(generated, str(path), sync_body=True), generated)

    def test_empty_local_body_is_replaced(self):
        path = self.root / "empty-body.md"
        path.write_text("---\n\ntitle: \"旧标题\"\n\n---\n\n", encoding="utf-8")
        generated = self._generated()
        self.assertEqual(compose_post(generated, str(path)), generated)


if __name__ == "__main__":
    unittest.main()
