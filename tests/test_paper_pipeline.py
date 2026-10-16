import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import notion_sync  # noqa: E402
from publish_paper_library import PipelineConfig, run_pipeline  # noqa: E402


class PaperPipelineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.data = self.root / "data"
        for name in ("papers", "summaries", "parsed"):
            (self.data / name).mkdir(parents=True)
        self.site = self.root / "site"
        (self.site / "source" / "_posts").mkdir(parents=True)
        self.exclusions = self.root / "exclusions.json"
        self.exclusions.write_text('{"excluded_ids": []}', encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def add_ready_paper(self, paper_id, title):
        (self.data / "papers" / f"{paper_id}.pdf").write_bytes(b"%PDF")
        parsed = self.data / "parsed" / f"{paper_id}_paper"
        parsed.mkdir()
        images = parsed / "images"
        images.mkdir()
        Image.new("RGB", (1280, 720), "white").save(images / "figure.png")
        (parsed / f"{paper_id}.md").write_text(
            f"# {title}\n\n## Abstract\nEvidence for {title}.\n\n"
            "## Method\nMethod evidence.\n\n"
            "![](images/figure.png)\nFigure 1: Fixture architecture.\n\n"
            "## References\n[1] Ref.\n",
            encoding="utf-8",
        )
        (self.data / "summaries" / f"{paper_id}_summary.md").write_text(
            f"# 摘要\n\n**英文标题**: {title}\n\n## 主要贡献\nEvidence.\n",
            encoding="utf-8",
        )

    def config(self, **changes):
        values = dict(
            library_root=self.root,
            site_root=self.site,
            exclusions=self.exclusions,
            batch="ready",
            ids=(),
            run_mineru=False,
            write_notion=False,
            promote=False,
            materialize=False,
            database_id="",
            token="",
            state_path=self.root / "state.json",
        )
        values.update(changes)
        return PipelineConfig(**values)

    def test_dry_run_is_sorted_and_does_not_write_state_or_site(self):
        self.add_ready_paper("2401.00002", "Second Paper")
        self.add_ready_paper("2401.00001", "First Paper")

        report = run_pipeline(self.config())

        self.assertEqual([item["arxiv_id"] for item in report["items"]], ["2401.00001", "2401.00002"])
        self.assertTrue(all(item["action"] == "dry_run" for item in report["items"]))
        self.assertEqual(report["items"][0]["title"], "摘要")
        self.assertEqual(report["items"][0]["figure_count"], 1)
        self.assertEqual(report["items"][0]["figure_provenance"], ["mineru_image"])
        self.assertTrue(report["items"][0]["source_pdf"])
        self.assertFalse((self.root / "state.json").exists())
        self.assertEqual(list((self.site / "source" / "_posts").glob("*.md")), [])

    def test_ids_filter_and_completed_state_are_respected(self):
        self.add_ready_paper("2401.00001", "First Paper")
        self.add_ready_paper("2401.00002", "Second Paper")
        (self.root / "state.json").write_text(
            json.dumps({"completed": ["2401.00001"]}), encoding="utf-8"
        )

        report = run_pipeline(self.config(ids=("2401.00001", "2401.00002")))

        self.assertEqual(report["items"][0]["action"], "skipped_completed")
        self.assertEqual(report["items"][1]["action"], "dry_run")

    def test_two_dry_runs_are_identical(self):
        self.add_ready_paper("2401.00001", "First Paper")

        first = run_pipeline(self.config())
        second = run_pipeline(self.config())

        self.assertEqual(first, second)

    def test_refresh_existing_rebuilds_a_materialized_paper_article(self):
        self.add_ready_paper("2401.00001", "First Paper")
        post = self.site / "source" / "_posts" / "paper-2401.00001.md"
        post.write_text(
            "---\narxiv_id: 2401.00001\n---\n\nlegacy generated body\n",
            encoding="utf-8",
        )

        report = run_pipeline(
            self.config(
                ids=("2401.00001",),
                refresh_existing=True,
                materialize=True,
                state_path=None,
            )
        )

        self.assertEqual(report["selected_count"], 1)
        self.assertEqual(report["items"][0]["action"], "materialized")
        self.assertIn("## 研究问题", post.read_text(encoding="utf-8"))

    def test_notion_file_block_becomes_pdf_link(self):
        block = {
            "type": "file",
            "file": {
                "name": "2401.00001.pdf",
                "external": {"url": "https://example.com/2401.00001.pdf"},
            },
        }

        self.assertEqual(
            notion_sync.block_to_md(block),
            "[2401.00001.pdf](https://example.com/2401.00001.pdf)",
        )

    def test_notion_image_caption_is_preserved_as_alt_text(self):
        block = {
            "type": "image",
            "image": {
                "caption": [{"plain_text": "Figure 1 architecture", "annotations": {}}],
                "external": {"url": "https://example.com/figure.png"},
            },
        }

        self.assertEqual(
            notion_sync.block_to_md(block),
            "![Figure 1 architecture](https://example.com/figure.png)",
        )

    def test_notion_arxiv_id_property_is_written_to_frontmatter(self):
        page = {
            "id": "page-id",
            "created_time": "2026-01-01T00:00:00Z",
            "properties": {
                "title": {"title": [{"plain_text": "Paper"}]},
                "arxiv_id": {"rich_text": [{"plain_text": "2401.00001"}]},
                "status": {"select": {"name": "Published"}},
                "type": {"select": {"name": "Post"}},
            },
        }
        with patch.object(notion_sync, "blocks_children", return_value=[]):
            markdown = notion_sync.page_to_md(page)

        self.assertIn('arxiv_id: "2401.00001"', markdown)


if __name__ == "__main__":
    unittest.main()
