import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from notion_content_audit import _download_with_retry, _normalize_text, audit_post  # noqa: E402
from notion_content_migration import parse_post  # noqa: E402


class AuditClient:
    def __init__(self, markdown, *, truncated=False, unknown=None):
        self.markdown = markdown
        self.truncated = truncated
        self.unknown = unknown or []

    def find_page_by_slug(self, database_id, slug):
        return {"id": "page-1"}

    def retrieve_markdown(self, page_id):
        return {
            "markdown": self.markdown,
            "truncated": self.truncated,
            "unknown_block_ids": self.unknown,
        }


class NotionContentAuditTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "source" / "_posts").mkdir(parents=True)
        (self.root / "source" / "images").mkdir(parents=True)
        self.image = self.root / "source" / "images" / "figure.png"
        self.image.write_bytes(b"image-bytes")
        post_path = self.root / "source" / "_posts" / "paper.md"
        post_path.write_text(
            "---\ntitle: Paper\nslug: paper\ndescription: Summary\n---\n"
            "Before.\n\n![Figure](/images/figure.png)\n\nAfter.\n",
            encoding="utf-8",
        )
        self.post = parse_post(post_path, self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_audit_redownloads_images_and_accepts_matching_content(self):
        client = AuditClient("Before.\n![Figure](https://files.example/figure)\nAfter.")

        result = audit_post(
            client,
            "database",
            self.post,
            download=lambda url: b"image-bytes",
        )

        self.assertTrue(result.verified)
        self.assertEqual(result.local_image_hashes, [hashlib.sha256(b"image-bytes").hexdigest()])
        self.assertEqual(result.remote_image_hashes, result.local_image_hashes)

    def test_text_only_audit_does_not_download_images(self):
        client = AuditClient("Before.\n![Figure](https://files.example/figure)\nAfter.")

        result = audit_post(
            client,
            "database",
            self.post,
            download=lambda url: self.fail("text-only audit must not download images"),
            verify_images=False,
        )

        self.assertTrue(result.verified)

    def test_audit_rejects_same_filename_with_different_bytes(self):
        client = AuditClient("Before.\n![Figure](https://files.example/figure.png)\nAfter.")

        result = audit_post(client, "database", self.post, download=lambda url: b"wrong")

        self.assertFalse(result.verified)
        self.assertIn("image_hash_mismatch", result.errors)

    def test_audit_rejects_truncated_notion_content(self):
        client = AuditClient("Before.\nAfter.", truncated=True, unknown=["block-1"])

        result = audit_post(client, "database", self.post, download=lambda url: b"")

        self.assertFalse(result.verified)
        self.assertIn("remote_content_truncated", result.errors)

    def test_normalization_accepts_notion_table_and_link_canonicalization(self):
        local = "| 数据集 | 结果 |\n|---|---|\n| Demo | **87.7%** |\nhttps://example.com"
        notion = (
            '<table header-row="true"><tr><td>数据集</td><td>结果</td></tr>'
            '<tr><td>Demo</td><td>**87.7%**</td></tr></table>\n'
            '[https://example.com](https://example.com)'
        )

        self.assertEqual(_normalize_text(local), _normalize_text(notion))

    def test_normalization_accepts_code_fence_language_and_escaped_punctuation(self):
        local = "```text\nR@{10,20}\n```"
        notion = "```plain text\nR@\\{10,20\\}\n```"

        self.assertEqual(_normalize_text(local), _normalize_text(notion))

    def test_image_download_retries_transient_ssl_failure(self):
        calls = []

        class Response:
            content = b"image"

            def raise_for_status(self):
                return None

        def flaky_get(url, timeout):
            calls.append(url)
            if len(calls) == 1:
                raise requests.exceptions.SSLError("temporary")
            return Response()

        result = _download_with_retry("https://files.example/image", request_get=flaky_get, backoff=0)

        self.assertEqual(result, b"image")
        self.assertEqual(len(calls), 2)

    def test_normalization_ignores_notion_hard_break_markers(self):
        self.assertEqual(
            _normalize_text("arXiv: 2601.22498\n期刊: ACM"),
            _normalize_text("arXiv: 2601.22498\n\\\n期刊: ACM"),
        )

    def test_normalization_accepts_escaped_inline_pipe(self):
        self.assertEqual(
            _normalize_text("arXiv: 2601 | 会议: ACM"),
            _normalize_text("arXiv: 2601 \\| 会议: ACM"),
        )

    def test_normalization_ignores_notion_table_cell_break_backslashes(self):
        self.assertEqual(
            _normalize_text("Formal definition of the task."),
            _normalize_text("\\\nFormal\\\n\\\ndefinition\\\n\\\nof\\\n\\\nthe\\\n\\\ntask.\\"),
        )

    def test_normalization_accepts_notion_auto_linked_domain(self):
        self.assertEqual(
            _normalize_text("Preprints.org 版本"),
            _normalize_text("[Preprints.org](http://Preprints.org) 版本"),
        )

    def test_normalization_accepts_html_entity_for_less_than(self):
        self.assertEqual(_normalize_text("交互 < 5 次"), _normalize_text("交互 &lt; 5 次"))

    def test_normalization_accepts_inline_code_protected_operator(self):
        self.assertEqual(_normalize_text("交互 < 5 次"), _normalize_text("交互 `<` 5 次"))

    def test_normalization_accepts_notion_expansion_of_relative_link(self):
        self.assertEqual(
            _normalize_text("[本地阅读](/papers/2403.06447.pdf)"),
            _normalize_text("[本地阅读](https://app.notion.com/papers/2403.06447.pdf)"),
        )

    def test_normalization_ignores_equivalent_math_delimiters(self):
        self.assertEqual(
            _normalize_text("$$W = F(u)$$"),
            _normalize_text("$W = F(u)$"),
        )

    def test_normalization_accepts_notion_subscript_tags_but_preserves_domain_tags(self):
        self.assertEqual(_normalize_text("KERAG_R_t"), _normalize_text("KERAG_R<sub>t"))
        self.assertEqual(_normalize_text("KERAG_R_t"), _normalize_text(r"KERAG_R\<sub\>t\</sub\>"))
        self.assertIn("<think>", _normalize_text("`<`think>内容`<`/think>"))

    def test_normalization_handles_double_escaped_notion_tags_and_visible_dash_placeholder(self):
        self.assertEqual(_normalize_text("<table><tr><td>X</td></tr></table>"), _normalize_text("&amp;lt;table&amp;gt;&amp;lt;tr&amp;gt;&amp;lt;td&amp;gt;X&amp;lt;/td&amp;gt;&amp;lt;/tr&amp;gt;&amp;lt;/table&amp;gt;"))
        self.assertEqual(_normalize_text("Value | - |"), _normalize_text("Value | — |"))

    def test_audit_records_remote_request_failure_without_crashing_batch(self):
        class FailedClient(AuditClient):
            def retrieve_markdown(self, page_id):
                raise requests.exceptions.SSLError("offline")

        result = audit_post(
            FailedClient(""),
            "database",
            self.post,
            page={"id": "page-1"},
        )

        self.assertFalse(result.verified)
        self.assertIn("remote_request_failed", result.errors)


if __name__ == "__main__":
    unittest.main()
