from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from paper_article import REQUIRED_SECTIONS
from review_adapter import AdapterError


class ReviewPackageEntrypointTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.image = self.root / "fig.png"
        Image.new("RGB", (1280, 720), "white").save(self.image)
        self.pdf = self.root / "paper.pdf"
        self.pdf.write_bytes(b"%PDF-test")
        self.raw = {"article_input": {"title": "Paper", "slug": "paper", "markdown":
            "\n".join(REQUIRED_SECTIONS) + "\n图示解释：架构", "arxiv_id": "2401.00001",
            "source_text": "evidence", "source_pdf": str(self.pdf), "source_spans": {},
            "figures": [{"path": str(self.image), "caption": "Architecture", "dimensions": [1280, 720],
                         "is_hd": True, "provenance": "fixture"}]},
            "facts": {"authors": []}, "references": [], "location": None, "formulae": [],
            "identity_status": "ready", "blog_compatibility": "not_validated", "review_status": "pending",
            "missing_fields": ["authors"]}
        self.path = self.root / "notion.json"
        self.write()

    def tearDown(self):
        self.temp.cleanup()

    def write(self):
        self.path.write_text(json.dumps(self.raw, ensure_ascii=False), encoding="utf-8")

    def test_dry_run_returns_draft_metadata_and_report_without_requests(self):
        from publish_review_package import run_review_package
        with patch("requests.sessions.Session.request", side_effect=AssertionError("network in dry run")):
            draft, meta, report = run_review_package(self.path)
        self.assertEqual(draft.title, "Paper")
        self.assertEqual(meta.references.status, "present_but_empty")
        self.assertEqual(report["mode"], "dry_run")
        self.assertEqual(report["article"]["title"], "Paper")
        self.assertEqual(report["identity"]["type"], "arxiv")
        self.assertEqual(report["identity"]["sources"], ["arxiv_id"])
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["warnings"], [])
        self.assertEqual(report["gate_stage"], "draft")
        self.assertEqual(report["metadata_status"]["location"], "missing")
        self.assertEqual(set(report["metadata_status"]), {"authors", "venue", "references", "location", "formulae"})

    def test_real_echo_package_reports_validation_errors_without_network(self):
        from publish_review_package import run_review_package
        path = Path("D:/recommendation-system-learning/data/blog_identity_tests_n/test_real_echomllm_assets_comp0/publish_queue/notion/4840fb51235a06ee8238ae1f792fb59e/notion.json")
        try:
            available = path.is_file()
        except PermissionError:
            available = False
        if not available:
            self.skipTest("optional local EchoMLLM package unavailable")
        with patch("requests.sessions.Session.request", side_effect=AssertionError("network in dry run")):
            draft, meta, report = run_review_package(path)
        self.assertEqual(draft.canonical_id, "2026.findings-acl.1001")
        self.assertEqual(report["identity"]["type"], "acl_doi")
        self.assertIn("doi", report["identity"]["sources"])
        self.assertTrue(report["errors"])
        self.assertEqual(meta.formulae.status, "present_but_empty")

    def test_missing_title_keeps_adapter_error_path(self):
        from publish_review_package import run_review_package
        del self.raw["article_input"]["title"]
        self.write()
        with self.assertRaisesRegex(AdapterError, r"\$\.article_input\.title"):
            run_review_package(self.path)

    def test_write_acl_reaches_publisher_without_local_guard(self):
        from publish_review_package import run_review_package
        from notion_publish import PublishResult
        self.raw["article_input"].update(arxiv_id="", doi="10.18653/v1/2026.findings-acl.1001")
        self.write()
        client = object()
        with patch("publish_review_package.publish_article",
                   return_value=PublishResult("", "created", "page-acl")) as publisher:
            _, _, report = run_review_package(
                self.path, write_notion=True, client=client, database_id="db")
        self.assertEqual(report["delivery"]["page_id"], "page-acl")
        publisher.assert_called_once()
        self.assertEqual(publisher.call_args.kwargs,
                         {"write": True, "promote": True, "allow_overwrite": False,
                          "skip_if_exists": True, "gate_stage": "draft", "metadata": {}})

    def test_write_valid_arxiv_calls_existing_publisher_without_promote(self):
        from publish_review_package import run_review_package
        from notion_publish import PublishResult
        client = object()
        with patch("publish_review_package.publish_article", return_value=PublishResult("2401.00001", "created", "page-1")) as publisher:
            _, _, report = run_review_package(self.path, write_notion=True, client=client, database_id="db")
        self.assertEqual(report["delivery"]["page_id"], "page-1")
        # Default publish promotes to homepage (status=Published).
        self.assertEqual(publisher.call_args.kwargs,
                         {"write": True, "promote": True, "allow_overwrite": False,
                          "skip_if_exists": True, "gate_stage": "draft", "metadata": {}})

    def test_draft_flag_keeps_page_invisible(self):
        from publish_review_package import run_review_package
        from notion_publish import PublishResult
        client = object()
        with patch("publish_review_package.publish_article", return_value=PublishResult("2401.00001", "created", "page-1")) as publisher:
            run_review_package(self.path, write_notion=True, client=client, database_id="db",
                               promote=False)
        self.assertFalse(publisher.call_args.kwargs["promote"])

    def test_verified_location_flows_into_publisher_kwargs(self):
        from publish_review_package import run_review_package
        from notion_publish import PublishResult
        self.raw["location"] = {"location_type": "affiliation", "venue_city": "Vienna",
                                "affil_city": ["Wuhan"], "corresponding_city": "Wuhan",
                                "affiliation_name": "Wuhan University",
                                "verification_status": "verified"}
        self.write()
        with patch("publish_review_package.publish_article",
                   return_value=PublishResult("2401.00001", "created", "page-1")) as publisher:
            run_review_package(self.path, write_notion=True, client=object(), database_id="db")
        kwargs = publisher.call_args.kwargs
        self.assertEqual(kwargs["location"]["venue_city"], "Vienna")
        self.assertEqual(kwargs["location"]["affil_city"], ["Wuhan"])

    def test_pending_location_is_not_passed_to_publisher(self):
        from publish_review_package import run_review_package
        from notion_publish import PublishResult
        self.raw["location"] = {"venue_city": "Vienna", "verification_status": "unverified"}
        self.write()
        with patch("publish_review_package.publish_article",
                   return_value=PublishResult("2401.00001", "created", "page-1")) as publisher:
            run_review_package(self.path, write_notion=True, client=object(), database_id="db")
        self.assertNotIn("location", publisher.call_args.kwargs)

    def test_publication_metadata_carries_date_authors_and_filters(self):
        from publish_review_package import run_review_package
        from notion_publish import PublishResult
        self.raw["facts"] = {
            "authors": [{"name": "Ada Lovelace"}, {"name": "Alan Turing"}],
            "published_date": "2026-10-04",
            "year": "2026",
            "venue_name": "SIGIR",
            "venue_type": "会议",
            "verification_status": "verified",
            "keywords": ["多模态推荐", "统一编码"],
            "categories": ["推荐系统", "多模态推荐"],
            "one_line": "一句话摘要",
        }
        self.write()
        with patch("publish_review_package.publish_article",
                   return_value=PublishResult("2401.00001", "created", "page-1")) as publisher:
            _, _, report = run_review_package(
                self.path, write_notion=True, client=object(), database_id="db")
        metadata = publisher.call_args.kwargs["metadata"]
        self.assertEqual(metadata["date"], "2026-10-04")
        self.assertEqual(metadata["authors"], "Ada Lovelace；Alan Turing")
        self.assertEqual(metadata["summary"], "一句话摘要")
        self.assertEqual(metadata["year"], "2026")
        self.assertEqual(metadata["venue_name"], "SIGIR")
        self.assertEqual(metadata["venue_type"], "会议")
        self.assertEqual(metadata["category"], "推荐系统 / 多模态推荐")
        self.assertEqual(metadata["tags"], ["多模态推荐", "统一编码"])
        self.assertEqual(report["publication_metadata"]["date"], "2026-10-04")

    def test_unverified_venue_is_not_written(self):
        from publish_review_package import run_review_package
        from notion_publish import PublishResult
        self.raw["facts"] = {"authors": [], "venue_name": "SIGIR", "venue_type": "会议",
                             "verification_status": "unverified"}
        self.write()
        with patch("publish_review_package.publish_article",
                   return_value=PublishResult("2401.00001", "created", "page-1")) as publisher:
            run_review_package(self.path, write_notion=True, client=object(), database_id="db")
        metadata = publisher.call_args.kwargs["metadata"]
        self.assertNotIn("venue_name", metadata)
        self.assertNotIn("venue_type", metadata)

    def test_cli_default_dry_run_prints_report_and_no_network(self):
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
        process = subprocess.run([sys.executable, str(ROOT / "tools" / "publish_review_package.py"),
                                  "--review-json", str(self.path)], capture_output=True, text=True,
                                 encoding="utf-8", env=env)
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertEqual(json.loads(process.stdout)["mode"], "dry_run")

    def test_cli_write_acl_reaches_publisher_or_credential_gate(self):
        self.raw["article_input"].update(arxiv_id="", doi="10.18653/v1/2026.findings-acl.1001")
        self.write()
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
        process = subprocess.run([sys.executable, str(ROOT / "tools" / "publish_review_package.py"),
                                  "--review-json", str(self.path), "--write-notion"],
                                 capture_output=True, text=True, encoding="utf-8", env=env,
                                 input="")
        self.assertNotIn("arXiv-only deduplication", process.stderr)
        self.assertNotIn("arXiv-only deduplication", process.stdout)


if __name__ == "__main__":
    unittest.main()
