import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from paper_inventory import build_manifest, write_manifest  # noqa: E402


class PaperInventoryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.papers = self.root / "papers"
        self.summaries = self.root / "summaries"
        self.parsed = self.root / "parsed"
        self.posts = self.root / "posts"
        for path in (self.papers, self.summaries, self.parsed, self.posts):
            path.mkdir()
        self.exclusions = self.root / "exclusions.json"
        self.exclusions.write_text(
            json.dumps({"excluded_ids": ["2504.00678", "2505.00556"]}),
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def add_paper(self, paper_id, parsed_title=None, summary_title=None):
        (self.papers / f"{paper_id}.pdf").write_bytes(b"%PDF-fixture")
        if parsed_title:
            folder = self.parsed / f"{paper_id}_paper"
            folder.mkdir()
            (folder / f"{paper_id}.md").write_text(
                f"# {parsed_title}\n\n## Abstract\nFixture abstract.", encoding="utf-8"
            )
        if summary_title:
            (self.summaries / f"{paper_id}_summary.md").write_text(
                f"# 摘要\n\n**英文标题**: {summary_title}\n", encoding="utf-8"
            )

    def test_assigns_each_publication_state(self):
        self.add_paper("2401.00001", "Ready Paper", "Ready Paper")
        self.add_paper("2401.00002", "Needs Summary")
        self.add_paper("2401.00003")
        self.add_paper("2401.00004", "Published Paper", "Published Paper")
        (self.posts / "published.md").write_text(
            "---\ntitle: Published\n---\nhttps://arxiv.org/abs/2401.00004\n",
            encoding="utf-8",
        )

        records = build_manifest(
            self.papers, self.summaries, self.parsed, self.posts, self.exclusions
        )

        self.assertEqual(
            {record.arxiv_id: record.quality_state for record in records},
            {
                "2401.00001": "ready",
                "2401.00002": "needs_summary",
                "2401.00003": "needs_parse",
                "2401.00004": "published",
            },
        )

    def test_rejects_duplicate_pdf_ids(self):
        self.add_paper("2401.00001", "Paper", "Paper")
        (self.papers / "2401.00001_copy.pdf").write_bytes(b"%PDF-copy")

        with self.assertRaisesRegex(ValueError, "duplicate PDF arXiv ID 2401.00001"):
            build_manifest(
                self.papers, self.summaries, self.parsed, self.posts, self.exclusions
            )

    def test_routes_title_mismatch_to_summary_regeneration(self):
        self.add_paper("2401.00001", "Authoritative Recommendation Paper", "Unrelated Algebra Theorem")

        record = build_manifest(
            self.papers, self.summaries, self.parsed, self.posts, self.exclusions
        )[0]

        self.assertEqual(record.quality_state, "needs_summary")
        self.assertIn("title mismatch", record.reasons)

    def test_inline_html_in_parsed_title_does_not_create_false_mismatch(self):
        self.add_paper(
            "2401.00001",
            "LenGuard-GPC: Len<sub>g</sub>th Guardin<sub>g w</sub>ith Guided-Prom<sub>p</sub>t Consistenc<sub>y</sub> for S<sub>p</sub>atial R<sub>easo</sub>nin<sub>g</sub> R<sub>e</sub>inf<sub>o</sub>r<sub>ce</sub> L<sub>ea</sub>rnin<sub>g</sub>",
            "LenGuard-GPC: Length Guarding with Guided-Prompt Consistency for Spatial Reasoning Reinforcement Learning",
        )

        record = build_manifest(
            self.papers, self.summaries, self.parsed, self.posts, self.exclusions
        )[0]

        self.assertEqual(record.quality_state, "ready")
        self.assertNotIn("title mismatch", record.reasons)

    def test_excluded_id_cannot_be_reintroduced(self):
        self.add_paper("2504.00678", "RapidPD", "RapidPD")

        records = build_manifest(
            self.papers, self.summaries, self.parsed, self.posts, self.exclusions
        )

        self.assertEqual(records, [])

    def test_manifest_json_is_stably_sorted(self):
        self.add_paper("2401.00002")
        self.add_paper("2401.00001")
        out = self.root / "manifest.json"

        write_manifest(
            build_manifest(
                self.papers, self.summaries, self.parsed, self.posts, self.exclusions
            ),
            out,
        )
        data = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual([item["arxiv_id"] for item in data["papers"]], ["2401.00001", "2401.00002"])

if __name__ == "__main__":
    unittest.main()
