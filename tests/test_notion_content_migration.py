import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from notion_content_migration import (  # noqa: E402
    ImagePart,
    TextPart,
    _select_posts,
    _notion_safe_markdown,
    build_migration_plan,
    build_orphan_asset_posts,
    migrate_post,
    parse_post,
)


class MemoryMigrationClient:
    def __init__(self):
        self.pages = {}
        self.uploads = []

    def find_page_by_slug(self, database_id, slug):
        return self.pages.get(slug)

    def create_page(self, database_id, properties):
        page_id = f"page-{len(self.pages) + 1}"
        self.pages[properties["slug"]] = {"id": page_id, "events": [], "properties": properties}
        return page_id

    def update_page(self, page_id, properties):
        return None

    def replace_markdown(self, page_id, markdown):
        page = next(item for item in self.pages.values() if item["id"] == page_id)
        page["events"] = [("markdown", markdown)]

    def append_markdown(self, page_id, markdown):
        page = next(item for item in self.pages.values() if item["id"] == page_id)
        page["events"].append(("markdown", markdown))

    def upload_file(self, path):
        self.uploads.append(Path(path).name)
        return f"upload-{Path(path).name}"

    def append_uploaded_image(self, page_id, upload_id, caption):
        page = next(item for item in self.pages.values() if item["id"] == page_id)
        page["events"].append(("image", upload_id, caption))


class NotionContentMigrationTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "source" / "_posts").mkdir(parents=True)
        (self.root / "source" / "images" / "papers" / "2401.00001").mkdir(parents=True)
        (self.root / "source" / "images" / "map").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write_post(self, body):
        path = self.root / "source" / "_posts" / "paper.md"
        path.write_text(body, encoding="utf-8")
        return path

    def test_parse_post_strips_frontmatter_and_preserves_image_order(self):
        image = self.root / "source" / "images" / "papers" / "2401.00001" / "figure.png"
        image.write_bytes(b"figure")
        post = self.write_post(
            "---\n"
            'title: "论文标题"\n'
            "slug: paper-2401.00001\n"
            'arxiv_id: "2401.00001"\n'
            'description: "摘要"\n'
            "---\n"
            "## 方法\n\n"
            "正文。\n\n"
            "![框架图](/images/papers/2401.00001/figure.png)\n\n"
            "## 实验\n\n结果。\n"
        )

        record = parse_post(post, self.root)

        self.assertEqual(record.title, "论文标题")
        self.assertEqual(record.slug, "paper-2401.00001")
        self.assertEqual(record.arxiv_id, "2401.00001")
        self.assertEqual([type(part) for part in record.parts], [TextPart, ImagePart, TextPart])
        self.assertNotIn("title:", record.parts[0].markdown)
        self.assertEqual(record.parts[1].path, image)
        self.assertEqual(record.parts[1].caption, "框架图")

    def test_plan_includes_all_images_deduplicates_bytes_and_rejects_oversize(self):
        referenced = self.root / "source" / "images" / "paper.png"
        referenced.write_bytes(b"same-image")
        duplicate = self.root / "source" / "images" / "map" / "city.png"
        duplicate.write_bytes(b"same-image")
        oversize = self.root / "source" / "images" / "map" / "huge.png"
        oversize.write_bytes(b"01234567890")
        self.write_post(
            "---\n"
            "title: Paper\n"
            "slug: paper\n"
            "description: Summary\n"
            "---\n"
            "Text.\n\n"
            "![Figure](/images/paper.png)\n"
        )

        plan = build_migration_plan(self.root, max_file_bytes=10)

        self.assertEqual(len(plan.posts), 1)
        self.assertEqual(len(plan.unique_assets), 1)
        self.assertEqual(plan.unique_assets[0].sha256, plan.posts[0].images[0].sha256)
        self.assertEqual(len(plan.orphan_images), 0)
        self.assertEqual([(item.path.name, item.reason) for item in plan.skipped], [("huge.png", "over_limit")])

    def test_valid_oversize_raster_is_compressed_into_upload_cache(self):
        image = self.root / "source" / "images" / "papers" / "2401.00001" / "large.png"
        pixels = bytes((index * 37) % 256 for index in range(180 * 180 * 3))
        Image.frombytes("RGB", (180, 180), pixels).save(image)
        self.write_post(
            "---\ntitle: Paper\nslug: paper\n---\n"
            "![Large](/images/papers/2401.00001/large.png)\n"
        )

        plan = build_migration_plan(self.root, max_file_bytes=700)

        self.assertEqual(plan.skipped, [])
        self.assertEqual(len(plan.posts[0].images), 1)
        self.assertLessEqual(plan.posts[0].images[0].size, 700)
        self.assertIn(".notion-migration-cache", str(plan.posts[0].images[0].path))

    def test_migrate_post_is_dry_run_by_default(self):
        image = self.root / "source" / "images" / "paper.png"
        image.write_bytes(b"image")
        record = parse_post(
            self.write_post(
                "---\ntitle: Paper\nslug: paper\ndescription: Summary\n---\n"
                "Before.\n\n![Figure](/images/paper.png)\n\nAfter.\n"
            ),
            self.root,
        )
        client = MemoryMigrationClient()

        result = migrate_post(client, "database", record, write=False)

        self.assertEqual(result.action, "dry_run")
        self.assertEqual(client.pages, {})
        self.assertEqual(client.uploads, [])

    def test_migrate_post_writes_markdown_and_images_in_source_order(self):
        image = self.root / "source" / "images" / "paper.png"
        image.write_bytes(b"image")
        record = parse_post(
            self.write_post(
                "---\ntitle: Paper\nslug: paper\ndescription: Summary\n---\n"
                "Before.\n\n![Figure](/images/paper.png)\n\nAfter.\n"
            ),
            self.root,
        )
        client = MemoryMigrationClient()

        result = migrate_post(client, "database", record, write=True)

        self.assertEqual(result.action, "created")
        self.assertEqual(client.uploads, ["paper.png"])
        self.assertEqual(
            client.pages["paper"]["events"],
            [
                ("markdown", "Before."),
                ("image", "upload-paper.png", "Figure"),
                ("markdown", "After."),
            ],
        )

    def test_orphan_images_are_grouped_into_hidden_asset_pages(self):
        for name, payload in (("one.jpg", b"one"), ("two.jpg", b"two"), ("three.jpg", b"three")):
            (self.root / "source" / "images" / "map" / name).write_bytes(payload)
        self.write_post("---\ntitle: Paper\nslug: paper\n---\nText.\n")
        plan = build_migration_plan(self.root)

        asset_posts = build_orphan_asset_posts(plan, group_size=2)

        self.assertEqual([post.slug for post in asset_posts], ["notion-assets-001", "notion-assets-002"])
        self.assertTrue(all(post.status == "Invisible" for post in asset_posts))
        self.assertEqual(
            sorted(image.sha256 for post in asset_posts for image in post.images),
            sorted(image.sha256 for image in plan.orphan_images),
        )

    def test_hidden_asset_page_stays_invisible_when_migrated(self):
        orphan = self.root / "source" / "images" / "map" / "city.jpg"
        orphan.write_bytes(b"city")
        self.write_post("---\ntitle: Paper\nslug: paper\n---\nText.\n")
        asset_post = build_orphan_asset_posts(build_migration_plan(self.root))[0]
        client = MemoryMigrationClient()

        migrate_post(client, "database", asset_post, write=True)

        self.assertEqual(client.pages[asset_post.slug]["properties"]["status"], "Invisible")

    def test_resume_selection_starts_at_requested_slug(self):
        posts = [
            type("Post", (), {"slug": slug})()
            for slug in ("one", "two", "three")
        ]

        selected = _select_posts(posts, start_at="two", limit=None, slugs=None)

        self.assertEqual([post.slug for post in selected], ["two", "three"])

    def test_selection_can_target_specific_slugs(self):
        posts = [type("Post", (), {"slug": slug})() for slug in ("one", "two", "three")]

        selected = _select_posts(posts, start_at=None, limit=None, slugs=["three", "one"])

        self.assertEqual([post.slug for post in selected], ["one", "three"])

    def test_notion_markdown_escapes_numeric_less_than_and_standalone_table_plus(self):
        markdown = "交互 < 5 次，前缀 <k\n<table><tr><td>保留</td></tr></table>\n\n| 模型 | 标记 |\n|---|---|\n| Demo | A + B |\n| Missing | - |\n| + 图像 | 1 |"

        safe = _notion_safe_markdown(markdown)

        self.assertIn("交互 `<` 5 次", safe)
        self.assertIn("前缀 `<`k", safe)
        self.assertIn("<table><tr><td>保留</td></tr></table>", safe)
        self.assertIn("| Demo | A `+` B |", safe)
        self.assertIn("| Missing | — |", safe)
        self.assertIn("| `+` 图像 |", safe)


if __name__ == "__main__":
    unittest.main()
