from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "backfill_venue.py"


class BackfillVenueTests(unittest.TestCase):
    def run_backfill(self, name: str, frontmatter: str) -> str:
        with tempfile.TemporaryDirectory() as temporary:
            post = Path(temporary) / name
            post.write_text(f"---\n{frontmatter}\n---\n\n正文\n", encoding="utf-8")
            subprocess.run(
                [sys.executable, str(SCRIPT), temporary, "--apply"],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            return post.read_text(encoding="utf-8")

    def test_verified_venue_replaces_existing_placeholder_metadata(self) -> None:
        updated = self.run_backfill(
            "lightgcl-svd-contrastive-view.md",
            "title: LightGCL\ndate: 2026-10-01\nyear: 2026\n"
            "venue_type: arXiv预印本\nvenue_name: arXiv",
        )

        self.assertIn("year: 2023", updated)
        self.assertIn("venue_type: 会议", updated)
        self.assertIn("venue_name: ICLR 2023", updated)

    def test_arxiv_identifier_supplies_real_preprint_year(self) -> None:
        updated = self.run_backfill(
            "paper-2407.18940.md",
            "title: LitSearch\ndate: 2026-10-19\nyear: 2026\n"
            "venue_type: arXiv预印本\nvenue_name: ''\nslug: paper-2407.18940",
        )

        self.assertIn("year: 2024", updated)
        self.assertIn("venue_type: arXiv预印本", updated)
        self.assertIn("venue_name: arXiv", updated)


if __name__ == "__main__":
    unittest.main()
