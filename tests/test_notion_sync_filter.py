import os
import tempfile
import unittest
from unittest.mock import patch

from tools import notion_sync
from tools.notion_sync import published_posts_query


class PublishedPostsQueryTests(unittest.TestCase):
    @staticmethod
    def _page(page_id, title, slug=""):
        return {
            "id": page_id,
            "created_time": "2026-10-20T00:00:00.000Z",
            "last_edited_time": "2026-10-20T00:00:00.000Z",
            "properties": {
                "title": {"title": [{"plain_text": title}]},
                "slug": {"rich_text": [{"plain_text": slug}]} if slug else {"rich_text": []},
                "status": {"select": {"name": "Published"}},
                "type": {"select": {"name": "Post"}},
            },
        }

    def test_query_requires_both_published_status_and_post_type(self):
        query = published_posts_query()

        self.assertEqual(
            query["filter"],
            {
                "and": [
                    {"property": "status", "select": {"equals": "Published"}},
                    {"property": "type", "select": {"equals": "Post"}},
                ]
            },
        )
        self.assertEqual(
            query["sorts"],
            [{"property": "date", "direction": "descending"}],
        )

    def test_new_query_is_not_mutated_by_previous_pagination(self):
        first = published_posts_query()
        first["start_cursor"] = "cursor-1"

        self.assertNotIn("start_cursor", published_posts_query())

    def test_full_sync_rejects_two_pages_resolving_to_same_slug(self):
        pages = [
            self._page("3fe59581-ebdd-0000-0000-000000000000", "Hello Rec", "hello-rec-3fb59581"),
            self._page("3fb59581-ebdd-0000-0000-000000000000", "hello-rec"),
        ]

        with patch.object(
            notion_sync,
            "api",
            return_value={"results": pages, "has_more": False},
        ):
            with self.assertRaisesRegex(ValueError, "slug collision"):
                list(notion_sync.iter_published_pages())

    def test_unchanged_state_regenerates_missing_markdown(self):
        page = self._page("page-1", "Paper", "paper-one")
        with tempfile.TemporaryDirectory() as directory:
            destination = os.path.join(directory, "paper-one.md")
            self.assertFalse(
                notion_sync.can_skip_unchanged_page(
                    page,
                    {"page-1": page["last_edited_time"]},
                    destination,
                )
            )

    def test_blank_notion_category_preserves_existing_frontmatter_categories(self):
        page = self._page("page-2", "Paper", "paper-two")
        with patch.object(notion_sync, "blocks_children", return_value=[]):
            rendered = notion_sync.page_to_md(
                page,
                fallback_categories=["推荐系统", "生成式推荐"],
            )

        self.assertIn('categories: ["推荐系统", "生成式推荐"]', rendered)
        self.assertNotIn("未分类", rendered)

    def test_existing_paper_date_is_preserved_when_notion_date_is_blank(self):
        page = self._page("page-3", "Paper", "paper-three")
        with patch.object(notion_sync, "blocks_children", return_value=[]):
            rendered = notion_sync.page_to_md(page, fallback_date="2025-04-17")

        self.assertIn('date: "2025-04-17"', rendered)
        self.assertNotIn('date: "2026-10-20"', rendered)

    def test_published_metadata_precedes_existing_date_and_created_time(self):
        page = self._page("page-4", "Paper", "paper-four")
        page["properties"]["published"] = {
            "rich_text": [{"plain_text": "2024-03-08T11:20:00Z"}]
        }
        with patch.object(notion_sync, "blocks_children", return_value=[]):
            rendered = notion_sync.page_to_md(page, fallback_date="2025-04-17")

        self.assertIn('date: "2024-03-08"', rendered)

    def test_frontmatter_date_reads_existing_hexo_source(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = os.path.join(directory, "paper.md")
            with open(destination, "w", encoding="utf-8") as handle:
                handle.write('---\ntitle: "Paper"\ndate: 2023-09-02\n---\n')

            self.assertEqual(notion_sync.frontmatter_date(destination), "2023-09-02")


if __name__ == "__main__":
    unittest.main()
