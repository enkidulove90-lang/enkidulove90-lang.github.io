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
from paper_article import (  # noqa: E402
    _first_sentence,
    build_article,
    materialize_article,
    validate_article,
)


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
            "## Benchmark 与数据集\n- Dataset-A\n\n"
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

    def test_chinese_lead_stops_at_first_sentence_without_whitespace(self):
        text = "第一句说明研究问题。第二句介绍完整方法。第三句给出实验结果。"

        self.assertEqual(_first_sentence(text), "第一句说明研究问题。")

    def test_builds_required_sections_links_and_figure_explanation(self):
        draft = build_article(self.record, self.parsed, self.summary)

        for heading in (
            "## 研究问题",
            "## 方法：核心思路与整体框架",
            "## 创新点",
            "## 实验：数据、基线与结果",
            "### 数据集与设置",
            "### Benchmark 与结果",
            "### 消融实验",
            "## 总结",
            "## References",
        ):
            self.assertIn(heading, draft.markdown)
        self.assertIn('title: "中文标题"', draft.markdown)
        self.assertIn('description: "本文研究可靠推荐，并在Dataset-A上提升12.5%。"', draft.markdown)
        self.assertIn("> 论文：", draft.markdown)
        self.assertIn("图示解释：", draft.markdown)
        self.assertIn("论文未报告独立的消融实验", draft.markdown)
        self.assertIn("https://arxiv.org/abs/2401.00001", draft.markdown)
        self.assertIn("https://github.com/example/evidence-rec", draft.markdown)
        self.assertIn("/papers/2401.00001.pdf", draft.markdown)
        self.assertEqual(validate_article(draft), [])

    def test_core_fact_provenance_missing_blocks_publication(self):
        base = build_article(self.record, self.parsed, self.summary)
        draft = replace(base, fact_provenance={"fields": {
            "paper_title": {"value": "T", "verification_status": "unverified"},
            "authors": {"value": [], "verification_status": "verified"},
            "venue_name": {"value": "ACL", "verification_status": "verified"},
            "year": {"value": "2026", "verification_status": "verified"},
            "identity": {"value": "2401.00001", "verification_status": "verified"},
        }})
        errors = validate_article(draft)
        self.assertTrue(any("paper_title" in error for error in errors), errors)

    def test_all_core_facts_verified_passes_gate(self):
        base = build_article(self.record, self.parsed, self.summary)
        fields = {name: {"value": "x", "verification_status": "verified"}
                  for name in ("paper_title", "authors", "venue_name", "year", "identity")}
        draft = replace(base, fact_provenance={"fields": fields})
        self.assertEqual(validate_article(draft), [])

    def test_references_with_links_flow_into_draft(self):
        base = build_article(self.record, self.parsed, self.summary)
        refs = [{"title": "Prior", "paper_url": "https://arxiv.org/abs/2401.00002",
                 "code_url": "https://github.com/x/y", "verification_status": "verified"}]
        draft = replace(base, references=refs)
        self.assertEqual(draft.references[0]["code_url"], "https://github.com/x/y")

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
        changed = replace(draft, markdown=draft.markdown.replace("## 总结", "## 其他"))

        self.assertIn("missing section: ## 总结", validate_article(changed))

    def test_chinese_summary_wins_over_english_mineru_sections(self):
        summary_without_conclusion = self.root / "summary-without-conclusion.md"
        summary_without_conclusion.write_text(
            self.summary.read_text(encoding="utf-8").replace(
                "# 中文标题\n\n",
                "# 中文方法标题\n\n**英文标题**: Metadata must not become the method.\n\n",
            ).replace(
                "\n## 实验结果\n相对Baseline取得12.5%的提升。\n\n",
                "\n## 实验效果\n相对Baseline取得12.5%的提升。\n\n"
                "## 实验条件\n"
                "- **数据与任务设置**：数据集：Dataset-A；任务：Experiments This English extraction must be removed.；划分：90/10\n"
                "- **基线与对照**：中文消融说明：移除证据校验模块后性能下降。\n\n",
            ).replace(
                "\n## 总结\n该方法改善了推荐可靠性。\n", "\n"
            ),
            encoding="utf-8",
        )
        parsed = replace(
            self.parsed,
            sections={
                "Abstract": "English abstract must not become the article lead.",
                "Method": "English method must not replace the Chinese explanation.",
                "Results": "English results must not replace the Chinese benchmark.",
                "Ablation": "English ablation must not replace the Chinese evidence.",
                "Conclusion": "English conclusion must not replace the Chinese summary.",
                "References": "[1] Example reference.",
            },
        )

        draft = build_article(self.record, parsed, summary_without_conclusion)

        self.assertIn("本文研究可靠推荐，并在Dataset-A上提升12.5%。", draft.markdown)
        self.assertIn("方法包含编码器与证据校验模块。", draft.markdown)
        self.assertNotIn("Metadata must not become the method", draft.markdown)
        self.assertIn("数据集：Dataset-A；划分：90/10", draft.markdown)
        self.assertNotIn("This English extraction must be removed", draft.markdown)
        self.assertIn("相对Baseline取得12.5%的提升。", draft.markdown)
        self.assertNotIn("English abstract must not", draft.markdown)
        self.assertNotIn("English method must not", draft.markdown)
        self.assertNotIn("English results must not", draft.markdown)
        self.assertIn("中文消融说明：移除证据校验模块后性能下降。", draft.markdown)
        self.assertNotIn("English ablation must not", draft.markdown)
        self.assertNotIn("English conclusion must not", draft.markdown)
        self.assertEqual(draft.source_spans["benchmark"], "summary:实验效果")
        self.assertEqual(draft.source_spans["ablation"], "summary:实验条件")
        self.assertEqual(draft.source_spans["conclusion"], "explicit absence")

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

    def test_materialize_acl_paper_uses_identity_key_path(self):
        base = build_article(self.record, self.parsed, self.summary)
        acl = replace(base, arxiv_id="", doi="10.18653/v1/2026.findings-acl.1001")
        site = self.root / "site-acl"

        post = materialize_article(acl, site)

        self.assertEqual(post.name, "paper-acl-2026-findings-acl-1001.md")
        self.assertTrue(post.exists())
        self.assertTrue(
            (site / "source" / "images" / "papers" / "acl-2026-findings-acl-1001" / "figure1.png").exists()
        )

    def test_existing_article_can_omit_source_pdf(self):
        draft = build_article(
            self.record, self.parsed, self.summary, include_source_pdf=False
        )

        self.assertIsNone(draft.source_pdf)
        self.assertNotIn("/papers/2401.00001.pdf", draft.markdown)
        self.assertEqual(validate_article(draft), [])

    def test_presentation_issues_warn_in_draft_but_block_in_publish(self):
        from paper_article import check_article
        base = build_article(self.record, self.parsed, self.summary)
        low_quality = replace(
            base,
            figures=[FigureAsset(path=self.image, caption="",
                                 dimensions=(320, 180), is_hd=False,
                                 provenance="mineru_image")],
        )
        draft_errors, draft_warnings = check_article(low_quality, stage="draft")
        publish_errors, _ = check_article(low_quality, stage="publish")
        # Presentation defects are warnings at draft stage, not blockers.
        self.assertFalse(any("non-HD" in e or "caption" in e for e in draft_errors))
        self.assertTrue(any("non-HD" in w for w in draft_warnings))
        self.assertTrue(any("caption" in w for w in draft_warnings))
        # At publish stage they become blockers.
        self.assertTrue(any("non-HD" in e for e in publish_errors))
        self.assertTrue(any("caption" in e for e in publish_errors))

    def test_unreviewed_manifest_figure_blocks_publish_warns_draft(self):
        from paper_article import check_article
        base = build_article(self.record, self.parsed, self.summary)
        unreviewed = replace(
            base,
            figures=[FigureAsset(path=self.image, caption="Figure 1",
                                 dimensions=(1280, 720), is_hd=True,
                                 provenance="mineru_image", manifest_sha256="abc123",
                                 visual_review="")],
        )
        _, draft_warnings = check_article(unreviewed, stage="draft")
        publish_errors, _ = check_article(unreviewed, stage="publish")
        self.assertTrue(any("unreviewed figure" in w for w in draft_warnings))
        self.assertTrue(any("unreviewed figure" in e for e in publish_errors))
        # A reviewed figure passes.
        reviewed = replace(unreviewed, figures=[
            replace(unreviewed.figures[0], visual_review="reviewed: caption verified")])
        self.assertFalse(any("unreviewed figure" in e
                             for e in check_article(reviewed, stage="publish")[0]))

    def test_truth_gap_blocks_even_at_draft_stage(self):
        from paper_article import check_article, CORE_FACT_FIELDS
        base = build_article(self.record, self.parsed, self.summary)
        provenance = {"fields": {
            name: {"verification_status": "verified"} for name in CORE_FACT_FIELDS
        }}
        provenance["fields"]["authors"]["verification_status"] = "unverified"
        gapped = replace(base, fact_provenance=provenance)
        draft_errors, _ = check_article(gapped, stage="draft")
        self.assertTrue(any("core fact unverified: authors" in e for e in draft_errors))


if __name__ == "__main__":
    unittest.main()
