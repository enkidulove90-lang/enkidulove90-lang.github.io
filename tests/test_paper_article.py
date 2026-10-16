import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from mineru_adapter import FigureAsset, ParsedPaper  # noqa: E402
from paper_article import build_article, materialize_article, validate_article  # noqa: E402


class PaperArticleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.pdf = self.root / "2401.00001.pdf"
        self.pdf.write_bytes(b"%PDF-source")
        self.image = self.root / "figure1.png"
        Image.new("RGB", (1280, 720), "white").save(self.image)
        self.summary = self.root / "summary.md"
        self.summary.write_text(
            "# 中文标题\n\n"
            "**英文标题**: Evidence Grounded Recommender\n\n"
            "## 主要贡献\n本文研究可靠推荐，并在Dataset-A上提升12.5%。\n\n"
            "## 方法论\n方法包含编码器与证据校验模块。\n\n"
            "## 创新点\n引入证据校验模块，避免无依据结论。\n\n"
            "## 数据集与实验设置\n选择Dataset-A进行实验。\n\n"
            "## 实验结果\n相对Baseline取得12.5%的提升。\n\n"
            "## 总结\n该方法改善了推荐可靠性。\n",
            encoding="utf-8",
        )
        self.record = SimpleNamespace(
            arxiv_id="2401.00001",
            pdf_path=str(self.pdf),
            parsed_title="Evidence Grounded Recommender",
            summary_title="Evidence Grounded Recommender",
        )
        self.parsed = ParsedPaper(
            arxiv_id="2401.00001",
            markdown_path=self.root / "paper.md",
            normalized_markdown=(
                "# Evidence Grounded Recommender\n\n## Abstract\nReliable recommendation.\n\n"
                "## Experiments\nDataset-A improves 12.5% over Baseline.\n\n"
                "Figure 1: Evidence verification architecture.\n\n"
                "## References\n[1] Example reference.\n"
                "https://github.com/example/evidence-rec"
            ),
            sections={"References": "[1] Example reference."},
            figures=[
                FigureAsset(
                    path=self.image,
                    caption="Figure 1: Evidence verification architecture.",
                    dimensions=(1280, 720),
                    is_hd=True,
                    provenance="mineru_image",
                )
            ],
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_builds_required_sections_links_and_figure_explanation(self):
        draft = build_article(self.record, self.parsed, self.summary)

        for heading in (
            "## 一、简介",
            "## 二、论文方法",
            "## 三、论文里的图与解释",
            "## 四、模块创新点",
            "## 五、实验数据集选择",
            "## 六、消融实验",
            "## 七、Benchmark 结果与解释",
            "## 八、总结",
            "## References",
        ):
            self.assertIn(heading, draft.markdown)
        self.assertIn("图示解释：", draft.markdown)
        self.assertIn("论文未报告独立的消融实验", draft.markdown)
        self.assertIn("https://arxiv.org/abs/2401.00001", draft.markdown)
        self.assertIn("https://github.com/example/evidence-rec", draft.markdown)
        self.assertIn("/papers/2401.00001.pdf", draft.markdown)
        self.assertEqual(validate_article(draft), [])

    def test_numeric_claim_not_present_in_sources_is_blocked(self):
        draft = build_article(self.record, self.parsed, self.summary)
        changed = replace(
            draft,
            markdown=draft.markdown.replace("改善了推荐可靠性", "改善了推荐可靠性并提升99.9%"),
        )

        self.assertIn("unsupported numeric claim: 99.9%", validate_article(changed))

    def test_internal_research_leak_is_blocked(self):
        draft = build_article(self.record, self.parsed, self.summary)
        changed = replace(draft, markdown=draft.markdown + "\n本课题的E14实验更好。\n")

        errors = validate_article(changed)

        self.assertIn("internal research marker: 本课题", errors)
        self.assertIn("internal research marker: E14", errors)

    def test_incomplete_draft_is_blocked(self):
        draft = build_article(self.record, self.parsed, self.summary)
        changed = replace(draft, markdown=draft.markdown.replace("## 八、总结", "## 其他"))

        self.assertIn("missing section: ## 八、总结", validate_article(changed))

    def test_article_without_hd_figure_is_blocked(self):
        parsed_without_figures = replace(self.parsed, figures=[])
        draft = build_article(self.record, parsed_without_figures, self.summary)

        self.assertIn("missing article figure", validate_article(draft))

    def test_materialize_copies_only_validated_assets(self):
        draft = build_article(self.record, self.parsed, self.summary)
        site = self.root / "site"

        post = materialize_article(draft, site)

        self.assertTrue(post.exists())
        self.assertTrue((site / "source" / "papers" / "2401.00001.pdf").exists())
        self.assertTrue(
            (site / "source" / "images" / "papers" / "2401.00001" / "figure1.png").exists()
        )

    def test_existing_article_can_omit_source_pdf(self):
        draft = build_article(
            self.record, self.parsed, self.summary, include_source_pdf=False
        )

        self.assertIsNone(draft.source_pdf)
        self.assertNotIn("/papers/2401.00001.pdf", draft.markdown)
        self.assertEqual(validate_article(draft), [])


if __name__ == "__main__":
    unittest.main()
