from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "source" / "_posts" / "verifiable-environments-lego-bricks.md"


class VerifiableEnvironmentsArticleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.article = ARTICLE.read_text(encoding="utf-8")

    def test_identity_and_real_publication_date(self):
        self.assertIn("date: 2026-06-10", self.article)
        self.assertIn('arxiv_id: "2606.12373"', self.article)
        self.assertNotIn("2026-10-19", self.article)

    def test_article_describes_reasoning_rl_instead_of_recommendation(self):
        self.assertNotIn("任务类型**: 序列推荐", self.article)
        self.assertIn("强化学习", self.article)
        self.assertIn("推理泛化", self.article)

    def test_official_figures_have_explanations(self):
        for filename in (
            "races-framework.png",
            "training-reward.png",
            "ood-performance.png",
            "composition-size.png",
        ):
            self.assertIn(f"/images/papers/2606.12373/{filename}", self.article)
        self.assertGreaterEqual(self.article.count("**图解：**"), 4)

    def test_main_results_preserve_all_baselines(self):
        for value in ("48.2", "48.8", "51.3", "58.8", "60.1", "61.1"):
            self.assertIn(value, self.article)
        self.assertIn("3.1", self.article)
        self.assertIn("2.5", self.article)

    def test_references_are_clickable_and_no_wiki_placeholders_remain(self):
        self.assertIn("## References", self.article)
        self.assertNotIn("[[", self.article)
        for url in (
            "https://arxiv.org/abs/2511.07317",
            "https://arxiv.org/abs/2601.04809",
            "https://openreview.net/forum?id=YcrOuJRVGh",
            "https://arxiv.org/abs/2602.12036",
        ):
            self.assertIn(url, self.article)


if __name__ == "__main__":
    unittest.main()
