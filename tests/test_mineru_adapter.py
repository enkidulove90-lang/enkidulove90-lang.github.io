import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import fitz
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from mineru_adapter import (  # noqa: E402
    MinerUUnavailable,
    ParseRequired,
    is_hd_image,
    prepare_assets,
)
from paper_inventory import build_manifest  # noqa: E402


class MinerUAdapterTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def record(self, parsed_md=None, pdf=None, paper_id="2401.00001"):
        return SimpleNamespace(
            arxiv_id=paper_id,
            parsed_md_path=str(parsed_md) if parsed_md else None,
            pdf_path=str(pdf or self.root / f"{paper_id}.pdf"),
        )

    def test_reuses_existing_markdown_and_matches_caption(self):
        parsed = self.root / "parsed"
        images = parsed / "images"
        images.mkdir(parents=True)
        Image.new("RGB", (1280, 700), "white").save(images / "architecture.png")
        md = parsed / "2401.00001.md"
        md.write_text(
            "# Paper\n\n## Method\n\n![](images/architecture.png)\n\n"
            "Figure 1: Overall architecture.\n",
            encoding="utf-8",
        )

        result = prepare_assets(self.record(md), self.root / "out", run_mineru=False)

        self.assertEqual(result.markdown_path, md.resolve())
        self.assertEqual(result.figures[0].caption, "Figure 1: Overall architecture.")
        self.assertEqual(result.figures[0].dimensions, (1280, 700))
        self.assertTrue(result.figures[0].is_hd)
        self.assertEqual(result.figures[0].provenance, "mineru_image")

    def test_matches_table_caption_for_rendered_table_image(self):
        parsed = self.root / "parsed"
        images = parsed / "images"
        images.mkdir(parents=True)
        Image.new("RGB", (800, 720), "white").save(images / "table.png")
        md = parsed / "2401.00001.md"
        md.write_text(
            "# Paper\n\n![](images/table.png)\nTable 16: Benchmark prompts.\n",
            encoding="utf-8",
        )

        result = prepare_assets(self.record(md), self.root / "out", run_mineru=False)

        self.assertEqual(result.figures[0].caption, "Table 16: Benchmark prompts.")

    def test_matches_caption_without_punctuation_after_number(self):
        parsed = self.root / "parsed"
        images = parsed / "images"
        images.mkdir(parents=True)
        Image.new("RGB", (1280, 720), "white").save(images / "figure.png")
        md = parsed / "2401.00001.md"
        md.write_text(
            "# Paper\n\n![](images/figure.png)\nFig. 1 Overview of the system.\n",
            encoding="utf-8",
        )

        result = prepare_assets(self.record(md), self.root / "out", run_mineru=False)

        self.assertEqual(result.figures[0].caption, "Fig. 1 Overview of the system.")

    def test_matches_appendix_figure_caption_with_letter(self):
        parsed = self.root / "parsed"
        images = parsed / "images"
        images.mkdir(parents=True)
        Image.new("RGB", (1280, 720), "white").save(images / "appendix.png")
        md = parsed / "2401.00001.md"
        md.write_text(
            "# Paper\n\n![](images/appendix.png)\n"
            "Figure C: Full remapping sweeps across Stage-1 budgets.\n",
            encoding="utf-8",
        )

        result = prepare_assets(self.record(md), self.root / "out", run_mineru=False)

        self.assertEqual(
            result.figures[0].caption,
            "Figure C: Full remapping sweeps across Stage-1 budgets.",
        )

    def test_reports_parse_required_without_opt_in(self):
        with self.assertRaises(ParseRequired):
            prepare_assets(self.record(), self.root / "out", run_mineru=False)

    def test_reports_missing_mineru_command_after_opt_in(self):
        with self.assertRaises(MinerUUnavailable):
            prepare_assets(
                self.record(),
                self.root / "out",
                run_mineru=True,
                command="definitely-not-a-real-mineru-command",
            )

    def test_hd_threshold_accepts_either_dimension(self):
        self.assertTrue(is_hd_image(1280, 400))
        self.assertTrue(is_hd_image(600, 720))
        self.assertFalse(is_hd_image(1279, 719))

    def test_uses_layout_crop_when_referenced_image_is_missing(self):
        parsed = self.root / "parsed"
        parsed.mkdir()
        pdf = parsed / "paper.pdf"
        doc = fitz.open()
        page = doc.new_page(width=600, height=800)
        page.draw_rect(fitz.Rect(50, 50, 300, 250), color=(0, 0, 0), fill=(0.9, 0.9, 0.9))
        doc.save(pdf)
        doc.close()
        layout = {
            "pdf_info": [
                {
                    "page_idx": 0,
                    "para_blocks": [
                        {"type": "image", "bbox": [50, 50, 300, 250]},
                        {
                            "type": "image_caption",
                            "bbox": [50, 260, 300, 285],
                            "lines": [{"spans": [{"content": "Figure 1: Vector architecture."}]}],
                        },
                    ],
                }
            ]
        }
        (parsed / "paper_layout.json").write_text(json.dumps(layout), encoding="utf-8")
        md = parsed / "2401.00001.md"
        md.write_text(
            "# Paper\n\n![](images/missing.png)\n\nFigure 1: Vector architecture.\n",
            encoding="utf-8",
        )

        result = prepare_assets(self.record(md, pdf), self.root / "out", run_mineru=False)

        self.assertEqual(len(result.figures), 1)
        self.assertTrue(result.figures[0].path.exists())
        self.assertEqual(result.figures[0].provenance, "layout_crop")
        self.assertIn("Figure 1", result.figures[0].caption)

    def test_uses_layout_crop_when_referenced_image_is_not_hd(self):
        parsed = self.root / "parsed"
        images = parsed / "images"
        images.mkdir(parents=True)
        Image.new("RGB", (500, 300), "white").save(images / "low-res.png")
        pdf = parsed / "paper.pdf"
        doc = fitz.open()
        page = doc.new_page(width=600, height=800)
        page.draw_rect(fitz.Rect(50, 80, 550, 420), color=(0, 0, 0), fill=(0.9, 0.9, 0.9))
        doc.save(pdf)
        doc.close()
        layout = {
            "pdf_info": [
                {
                    "page_idx": 0,
                    "para_blocks": [
                        {"type": "image", "bbox": [50, 80, 550, 420]},
                        {
                            "type": "image_caption",
                            "bbox": [50, 430, 550, 455],
                            "lines": [{"spans": [{"content": "Figure 1: Full architecture."}]}],
                        },
                    ],
                }
            ]
        }
        (parsed / "paper_layout.json").write_text(json.dumps(layout), encoding="utf-8")
        md = parsed / "2401.00001.md"
        md.write_text(
            "# Paper\n\n![](images/low-res.png)\nFigure 1: Full architecture.\n",
            encoding="utf-8",
        )

        result = prepare_assets(self.record(md, pdf), self.root / "out", run_mineru=False)

        self.assertTrue(any(figure.is_hd for figure in result.figures))
        self.assertTrue(any(figure.provenance == "layout_crop" for figure in result.figures))

    def test_prefers_cached_arxiv_source_before_layout_or_pdf_crop(self):
        parsed = self.root / "parsed"
        parsed.mkdir()
        pdf = parsed / "paper.pdf"
        doc = fitz.open()
        doc.new_page(width=600, height=800)
        doc.save(pdf)
        doc.close()
        md = parsed / "2401.00001.md"
        md.write_text("# Paper\n\n## Method\nSource text only.\n", encoding="utf-8")

        source = self.root / "out" / "2401.00001" / "arxiv-source" / "unpacked"
        (source / "figures").mkdir(parents=True)
        Image.new("RGB", (1800, 1000), "white").save(source / "figures" / "method.png")
        (source / "main.tex").write_text(
            "\\begin{figure}\\includegraphics{figures/method}"
            "\\caption{Figure 1: Author source architecture.}\\end{figure}",
            encoding="utf-8",
        )

        result = prepare_assets(self.record(md, pdf), self.root / "out", run_mineru=False)

        self.assertEqual(result.figures[0].provenance, "arxiv_source")
        self.assertIn("Author source architecture", result.figures[0].caption)

    def test_uses_pdf_caption_crop_when_markdown_has_no_images(self):
        parsed = self.root / "parsed"
        parsed.mkdir()
        pdf = parsed / "paper.pdf"
        doc = fitz.open()
        page = doc.new_page(width=600, height=800)
        page.insert_text((50, 120), "Method overview", fontsize=12)
        page.draw_rect(fitz.Rect(60, 220, 540, 500), color=(0, 0, 0), fill=(0.85, 0.9, 0.95))
        page.insert_text((60, 530), "Figure 1: Architecture from the source PDF.", fontsize=11)
        doc.save(pdf)
        doc.close()
        md = parsed / "2401.00001.md"
        md.write_text("# Paper\n\n## Method\nSource text only.\n", encoding="utf-8")

        result = prepare_assets(self.record(md, pdf), self.root / "out", run_mineru=False)

        self.assertTrue(any(figure.is_hd for figure in result.figures))
        self.assertEqual(result.figures[0].provenance, "pdf_caption_crop")
        self.assertIn("Figure 1", result.figures[0].caption)

    def test_real_manifest_contains_exactly_seven_parse_jobs(self):
        library = Path("D:/recommendation-system-learning/data")
        if not library.exists():
            self.skipTest("local paper library is not available")
        records = build_manifest(
            library / "papers",
            library / "summaries",
            library / "parsed",
            ROOT / "source" / "_posts",
            ROOT / "tools" / "paper_exclusions.json",
        )

        parse_ids = [record.arxiv_id for record in records if record.quality_state == "needs_parse"]

        self.assertEqual(
            parse_ids,
            [
                "2402.01135",
                "2402.13750",
                "2403.05668",
                "2410.23180",
                "2412.11068",
                "2602.15659",
                "2605.18805",
            ],
        )


if __name__ == "__main__":
    unittest.main()
