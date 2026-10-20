import sys
import tempfile
import unittest
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from mineru_adapter import FigureAsset  # noqa: E402
from notion_publish import NotionClient, publish_article  # noqa: E402
from paper_article import ArticleDraft  # noqa: E402


class MemoryClient:
    def __init__(self, existing=None):
        self.page = existing
        self.created = 0
        self.uploaded = []
        self.batches = []
        self.properties = None

    def find_page_by_arxiv(self, database_id, arxiv_id):
        return self.page

    def create_page(self, database_id, properties):
        self.created += 1
        self.properties = properties
        self.page = {"id": "page-1", "has_source_pdf": False}
        return "page-1"

    def update_page(self, page_id, properties):
        self.properties = properties

    def clear_children(self, page_id):
        self.batches.clear()

    def append_children(self, page_id, blocks):
        self.batches.append(list(blocks))

    def upload_file(self, path):
        self.uploaded.append(Path(path).name)
        return f"upload-{Path(path).name}"


class RecordingTransport:
    def __init__(self):
        self.calls = []
        self.counter = 0

    def request(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        if method == "POST" and path == "/file_uploads":
            self.counter += 1
            return {"id": f"file-{self.counter}"}
        return {"status": "ok"}


class SchemaTransport(RecordingTransport):
    def request(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        if method == "GET" and path == "/databases/database":
            return {"data_sources": [{"id": "source"}]}
        if method == "GET" and path == "/data_sources/source":
            return {
                "properties": {
                    "title": {"type": "title"},
                    "slug": {"type": "rich_text"},
                    "status": {"type": "select"},
                    "type": {"type": "select"},
                }
            }
        if method == "POST" and path == "/pages":
            return {"id": "page-1"}
        return {"results": []}


class FlakyTransport:
    def __init__(self):
        self.calls = 0

    def request(self, method, path, **kwargs):
        self.calls += 1
        if self.calls == 1:
            raise requests.exceptions.SSLError("temporary EOF")
        return {"markdown": "ok"}


class PageListTransport(SchemaTransport):
    def request(self, method, path, **kwargs):
        if method == "POST" and path == "/data_sources/source/query":
            self.calls.append((method, path, kwargs))
            return {
                "results": [
                    {
                        "id": "page-1",
                        "properties": {
                            "slug": {"rich_text": [{"plain_text": "paper-one"}]}
                        },
                    }
                ],
                "has_more": False,
            }
        return super().request(method, path, **kwargs)


class NotionPublishTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.pdf = self.root / "paper.pdf"
        self.pdf.write_bytes(b"pdf")
        self.image = self.root / "figure.png"
        self.image.write_bytes(b"png")

    def tearDown(self):
        self.tmp.cleanup()

    def draft(self, paragraphs=1, source_pdf=True):
        required = [
            "## 研究问题",
            "## 方法：核心思路与整体框架",
            "## 创新点",
            "## 实验：数据、基线与结果",
            "### 数据集与设置",
            "### Benchmark 与结果",
            "### 消融实验",
            "## 总结",
            "## References",
            "https://arxiv.org/abs/2401.00001",
        ]
        body = "\n\n".join(
            required
            + [
                "![Figure 1](/images/papers/2401.00001/figure.png)",
                "图示解释：Fixture figure.",
            ]
            + [f"paragraph {index}" for index in range(paragraphs)]
        )
        return ArticleDraft(
            arxiv_id="2401.00001",
            title="Paper",
            slug="paper-2401.00001",
            markdown=body,
            source_text=body,
            figures=[
                FigureAsset(
                    path=self.image,
                    caption="Figure 1: Fixture architecture.",
                    dimensions=(1280, 720),
                    is_hd=True,
                    provenance="mineru_image",
                )
            ],
            source_pdf=self.pdf if source_pdf else None,
        )

    def test_no_token_dry_run_makes_no_external_request(self):
        result = publish_article(None, self.draft(), "database", write=False)

        self.assertEqual(result.action, "dry_run")
        self.assertEqual(result.arxiv_id, "2401.00001")

    def test_create_is_idempotent_and_defaults_to_invisible(self):
        client = MemoryClient()

        first = publish_article(client, self.draft(), "database", write=True)
        second = publish_article(client, self.draft(), "database", write=True)

        self.assertEqual(first.page_id, "page-1")
        self.assertEqual(second.page_id, "page-1")
        self.assertEqual(client.created, 1)
        self.assertEqual(client.properties["status"], "Invisible")

    def test_promote_sets_published_status(self):
        client = MemoryClient()

        publish_article(client, self.draft(), "database", write=True, promote=True)

        self.assertEqual(client.properties["status"], "Published")

    def test_existing_page_without_pdf_is_not_backfilled(self):
        client = MemoryClient(existing={"id": "page-existing", "has_source_pdf": False})

        publish_article(client, self.draft(source_pdf=True), "database", write=True)

        self.assertNotIn("paper.pdf", client.uploaded)

    def test_new_page_with_pdf_uploads_source_file(self):
        client = MemoryClient()

        publish_article(client, self.draft(source_pdf=True), "database", write=True)

        self.assertIn("paper.pdf", client.uploaded)
        self.assertTrue(any(block.get("type") == "file" for batch in client.batches for block in batch))

    def test_blocks_are_chunked_at_one_hundred(self):
        client = MemoryClient()

        publish_article(client, self.draft(paragraphs=195, source_pdf=False), "database", write=True)

        self.assertEqual([len(batch) for batch in client.batches], [100, 100, 7])

    def test_small_file_uses_single_part_and_upload_cache(self):
        transport = RecordingTransport()
        client = NotionClient("secret", transport=transport, multipart_threshold=20)

        first = client.upload_file(self.pdf)
        second = client.upload_file(self.pdf)

        self.assertEqual(first, second)
        create_calls = [call for call in transport.calls if call[1] == "/file_uploads"]
        send_calls = [call for call in transport.calls if call[1].endswith("/send")]
        complete_calls = [call for call in transport.calls if call[1].endswith("/complete")]
        self.assertEqual(create_calls[0][2]["json"]["mode"], "single_part")
        self.assertEqual(len(create_calls), 1)
        self.assertEqual(len(send_calls), 1)
        self.assertEqual(len(complete_calls), 0)

    def test_large_file_uses_multipart_and_complete(self):
        large = self.root / "large.pdf"
        large.write_bytes(b"01234567890")
        transport = RecordingTransport()
        client = NotionClient(
            "secret", transport=transport, multipart_threshold=10, part_size=6
        )

        client.upload_file(large)

        create = next(call for call in transport.calls if call[1] == "/file_uploads")
        sends = [call for call in transport.calls if call[1].endswith("/send")]
        completes = [call for call in transport.calls if call[1].endswith("/complete")]
        self.assertEqual(create[2]["json"]["mode"], "multi_part")
        self.assertEqual(create[2]["json"]["number_of_parts"], 2)
        self.assertEqual([call[2]["data"]["part_number"] for call in sends], [1, 2])
        self.assertEqual(len(completes), 1)

    def test_find_page_by_slug_queries_the_slug_property(self):
        transport = RecordingTransport()
        client = NotionClient("secret", transport=transport)

        result = client.find_page_by_slug("database", "hello-rec")

        self.assertIsNone(result)
        query = next(call for call in transport.calls if call[1].endswith("/query"))
        self.assertEqual(
            query[2]["json"]["filter"],
            {"property": "slug", "rich_text": {"equals": "hello-rec"}},
        )

    def test_markdown_and_uploaded_image_methods_use_order_preserving_endpoints(self):
        transport = RecordingTransport()
        client = NotionClient("secret", transport=transport)

        client.replace_markdown("page-1", "Before")
        client.append_uploaded_image("page-1", "file-1", "Figure")
        client.append_markdown("page-1", "After")

        self.assertEqual(
            transport.calls,
            [
                (
                    "PATCH",
                    "/pages/page-1/markdown",
                    {"json": {"type": "replace_content", "replace_content": {"new_str": "Before"}}},
                ),
                (
                    "PATCH",
                    "/blocks/page-1/children",
                    {
                        "json": {
                            "children": [
                                {
                                    "object": "block",
                                    "type": "image",
                                    "image": {
                                        "type": "file_upload",
                                        "file_upload": {"id": "file-1"},
                                        "caption": [
                                            {"type": "text", "text": {"content": "Figure"}}
                                        ],
                                    },
                                }
                            ]
                        }
                    },
                ),
                (
                    "PATCH",
                    "/pages/page-1/markdown",
                    {
                        "json": {
                            "type": "insert_content",
                            "insert_content": {"content": "After", "position": {"type": "end"}},
                        }
                    },
                ),
            ],
        )

    def test_retrieve_markdown_uses_enhanced_markdown_endpoint(self):
        transport = RecordingTransport()
        client = NotionClient("secret", transport=transport)

        client.retrieve_markdown("page-1")

        self.assertEqual(
            transport.calls,
            [("GET", "/pages/page-1/markdown", {})],
        )

    def test_create_filters_optional_properties_against_live_schema(self):
        transport = SchemaTransport()
        client = NotionClient("secret", transport=transport)

        client.create_page(
            "database",
            {
                "title": "Paper",
                "slug": "paper",
                "status": "Published",
                "summary": "Not available in this database",
                "arxiv_id": "2401.00001",
            },
        )

        create = next(call for call in transport.calls if call[1] == "/pages")
        self.assertEqual(
            set(create[2]["json"]["properties"]),
            {"title", "slug", "status", "type"},
        )

    def test_transient_network_failure_is_retried(self):
        transport = FlakyTransport()
        client = NotionClient("secret", transport=transport, retry_backoff=0)

        result = client.retrieve_markdown("page-1")

        self.assertEqual(result, {"markdown": "ok"})
        self.assertEqual(transport.calls, 2)

    def test_list_pages_by_slug_queries_database_once(self):
        transport = PageListTransport()
        client = NotionClient("secret", transport=transport)

        pages = client.list_pages_by_slug("database")

        self.assertEqual(pages, {"paper-one": {"id": "page-1"}})
        queries = [call for call in transport.calls if call[1].endswith("/query")]
        self.assertEqual(len(queries), 1)


if __name__ == "__main__":
    unittest.main()
