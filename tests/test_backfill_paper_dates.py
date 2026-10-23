from __future__ import annotations

import sys
import unittest
from pathlib import Path


TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from backfill_paper_dates import (
    apply_publication_date,
    crossref_publication_date,
    datacite_publication_date,
    extract_identity,
    override_publication_date,
    parse_arxiv_dates,
)


class PaperDateBackfillTests(unittest.TestCase):
    def test_extracts_arxiv_or_doi_identity_from_post(self) -> None:
        arxiv = "---\narxiv_id: 2606.12373\n---\n"
        doi = "> 论文：[DOI](https://doi.org/10.1007/s44443-025-00026-1)"

        self.assertEqual(extract_identity(arxiv), ("arxiv", "2606.12373"))
        self.assertEqual(
            extract_identity(doi),
            ("doi", "10.1007/s44443-025-00026-1"),
        )

    def test_parses_exact_arxiv_submission_date(self) -> None:
        feed = """<feed xmlns="http://www.w3.org/2005/Atom">
          <entry>
            <id>http://arxiv.org/abs/2606.12373v1</id>
            <published>2026-06-10T17:39:41Z</published>
          </entry>
        </feed>"""

        self.assertEqual(parse_arxiv_dates(feed), {"2606.12373": "2026-06-10"})

    def test_replaces_only_frontmatter_date(self) -> None:
        post = "---\ntitle: paper\ndate: 2026-10-19\nyear: 2026\n---\nbody 2026-10-19\n"

        updated = apply_publication_date(post, "2026-06-10")

        self.assertIn("date: 2026-06-10", updated)
        self.assertIn("body 2026-10-19", updated)

    def test_crossref_prefers_online_publication_date(self) -> None:
        message = {
            "published-online": {"date-parts": [[2025, 12, 3]]},
            "created": {"date-parts": [[2025, 12, 8]]},
        }

        self.assertEqual(crossref_publication_date(message), "2025-12-03")

    def test_datacite_reads_published_date(self) -> None:
        attributes = {
            "published": "2026-01-14",
            "created": "2026-01-15T03:00:00Z",
        }

        self.assertEqual(datacite_publication_date(attributes), "2026-01-14")

    def test_audited_override_requires_date_and_source(self) -> None:
        overrides = {
            "10.example/paper": {
                "date": "2025-12-20",
                "source": "https://publisher.example/paper/v2",
            }
        }

        self.assertEqual(
            override_publication_date(overrides, "10.example/paper"),
            "2025-12-20",
        )
        self.assertEqual(override_publication_date({"10.example/bad": {"date": "2025"}}, "10.example/bad"), "")


if __name__ == "__main__":
    unittest.main()
