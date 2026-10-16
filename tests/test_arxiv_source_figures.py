import sys
import tempfile
import unittest
from pathlib import Path

import fitz
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from arxiv_source_figures import SourceFigure, extract_source_figures, select_source_figures  # noqa: E402


class ArxivSourceFiguresTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_extracts_includegraphics_with_figure_caption(self):
        source = self.root / "source"
        figures = source / "figures"
        figures.mkdir(parents=True)
        Image.new("RGB", (1600, 900), "white").save(figures / "architecture.png")
        (source / "main.tex").write_text(
            r"""
            \documentclass{article}
            \begin{document}
            \begin{figure*}
              \centering
              \includegraphics[width=\textwidth]{figures/architecture}
              \caption{The proposed architecture and its training stages.}
              \label{fig:architecture}
            \end{figure*}
            \end{document}
            """,
            encoding="utf-8",
        )

        assets = extract_source_figures(source, self.root / "out")

        self.assertEqual(len(assets), 1)
        self.assertEqual(assets[0].caption, "The proposed architecture and its training stages.")
        self.assertEqual(assets[0].dimensions, (1600, 900))
        self.assertTrue(assets[0].is_hd)
        self.assertEqual(assets[0].provenance, "arxiv_source")
        self.assertTrue(assets[0].path.exists())

    def test_applies_document_graphicspath_to_included_tex_file(self):
        source = self.root / "source"
        images = source / "imgs"
        images.mkdir(parents=True)
        image_pdf = fitz.open()
        image_pdf.new_page(width=500, height=300)
        image_pdf.save(images / "method.pdf")
        image_pdf.close()
        (source / "main.tex").write_text(
            r"\graphicspath{{imgs/}{./}}\input{body}", encoding="utf-8"
        )
        (source / "body.tex").write_text(
            r"\begin{figure}\includegraphics{method}"
            r"\caption{A \textbf{clean} method figure.}\end{figure}",
            encoding="utf-8",
        )

        assets = extract_source_figures(source, self.root / "out")

        self.assertEqual(len(assets), 1)
        self.assertEqual(assets[0].caption, "A clean method figure.")
        self.assertTrue(assets[0].is_hd)

    def test_selects_method_result_and_supplementary_source_figures(self):
        def figure(name, caption):
            return SourceFigure(
                path=self.root / name,
                caption=caption,
                dimensions=(1600, 900),
                is_hd=True,
            )

        assets = [
            figure("qualitative.png", "Qualitative examples."),
            figure("framework.png", "Overview of the proposed framework."),
            figure("ablation.png", "Ablation and benchmark results."),
            figure("extra.png", "Additional examples."),
        ]

        selected = select_source_figures(assets, limit=3)

        self.assertEqual(
            [item.path.name for item in selected],
            ["qualitative.png", "framework.png", "ablation.png"],
        )

    def test_transparent_source_image_is_composited_on_white(self):
        source = self.root / "source"
        source.mkdir()
        transparent = Image.new("RGBA", (1600, 900), (0, 0, 0, 0))
        transparent.putpixel((800, 450), (255, 0, 0, 255))
        transparent.save(source / "diagram.png")
        (source / "main.tex").write_text(
            r"\begin{figure}\includegraphics{diagram}"
            r"\caption{Transparent architecture.}\end{figure}",
            encoding="utf-8",
        )

        assets = extract_source_figures(source, self.root / "out")

        with Image.open(assets[0].path) as rendered:
            self.assertEqual(rendered.getpixel((0, 0)), (255, 255, 255))

    def test_caption_keeps_escaped_percent(self):
        source = self.root / "source"
        source.mkdir()
        Image.new("RGB", (1600, 900), "white").save(source / "result.png")
        (source / "main.tex").write_text(
            r"\begin{figure}\includegraphics{result}"
            r"\caption{Pass rate improves from 15\% to 45\%.}\end{figure}",
            encoding="utf-8",
        )

        assets = extract_source_figures(source, self.root / "out")

        self.assertEqual(assets[0].caption, "Pass rate improves from 15% to 45%.")


if __name__ == "__main__":
    unittest.main()
