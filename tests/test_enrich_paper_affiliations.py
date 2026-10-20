import importlib.util
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "enrich_paper_affiliations", ROOT / "tools" / "enrich_paper_affiliations.py"
)
enrich = importlib.util.module_from_spec(SPEC)


class EnrichPaperAffiliationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SPEC.loader.exec_module(enrich)

    def test_ar5iv_header_extracts_first_author_institution_and_city(self):
        html = """
        <span class="ltx_creator ltx_role_author">
          <span class="ltx_personname">Junda Wu</span>
          <span class="ltx_contact ltx_role_affiliation">
            <span class="ltx_contact_name">Affiliation:</span>
            <span class="ltx_text ltx_affiliation_institution">University of California San Diego</span>,
            <span class="ltx_text ltx_affiliation_city">La Jolla</span>,
            <span class="ltx_text ltx_affiliation_country">USA</span>
          </span>
        </span>
        """

        record = enrich.parse_first_author_affiliation(html)

        self.assertEqual(record["first_author"], "Junda Wu")
        self.assertEqual(record["affiliation_name"], "University of California San Diego")
        self.assertEqual(record["affil_city"], "La Jolla")
        self.assertEqual(record["country"], "USA")

    def test_arxiv_id_is_read_from_article_link(self):
        raw = "论文链接：https://arxiv.org/abs/2403.06447v2"
        self.assertEqual(enrich.extract_arxiv_id(raw), "2403.06447")

    def test_crossref_metadata_extracts_first_author_affiliation(self):
        payload = {"message": {"author": [{
            "given": "Jane", "family": "Doe",
            "affiliation": [{"name": "University of Bari Aldo Moro"}],
        }]}}

        record = enrich.parse_crossref_affiliation(payload)

        self.assertEqual(record["first_author"], "Jane Doe")
        self.assertEqual(record["affiliation_name"], "University of Bari Aldo Moro")

    def test_local_parsed_header_extracts_numbered_first_affiliation(self):
        raw = """
        ## Page 1
        # Autonomous Information Seeking
        Xinyu Lin<sup>1</sup> Yashar Deldjoo<sup>2</sup>
        <sup>1</sup>National University of Singapore <sup>2</sup>Polytechnic University of Bari
        ## 1. Introduction
        """

        record = enrich.parse_local_paper_header(raw)

        self.assertEqual(record["first_author"], "Xinyu Lin")
        self.assertEqual(record["affiliation_name"], "National University of Singapore")

    def test_shared_author_affiliation_is_used_when_first_author_span_has_none(self):
        html = """
        <div class="ltx_authors">
          <span class="ltx_creator ltx_role_author"><span class="ltx_personname">Xuheng Cai</span></span>
          <span class="ltx_creator ltx_role_author"><span class="ltx_personname">Xubin Ren</span>
            <span class="ltx_contact ltx_role_affiliation">Department of Computer Science, University of Hong Kong</span>
          </span>
        </div>
        """

        record = enrich.parse_first_author_affiliation(html)

        self.assertEqual(record["first_author"], "Xuheng Cai")
        self.assertEqual(record["affiliation_name"], "Department of Computer Science, University of Hong Kong")

    def test_affiliation_normalization_rejects_author_names_and_extracts_real_institution(self):
        self.assertEqual(enrich.normalize_affiliation("Weizhi Zhang"), "")
        self.assertEqual(
            enrich.normalize_affiliation("Alejandro Godinez Department of Environmental Health Sciences University at Albany, State University of New York Albany"),
            "University at Albany",
        )
        self.assertEqual(enrich.normalize_affiliation("2 ShanghaiTech University"), "ShanghaiTech University")

    def test_affiliation_normalization_preserves_complete_academic_names(self):
        complete_names = (
            "Southern University of Science and Technology",
            "Beijing University of Posts and Telecommunications",
            "National University of Singapore",
            "Technical University of Munich",
            "University of Chinese Academy of Sciences",
        )

        for name in complete_names:
            with self.subTest(name=name):
                self.assertEqual(enrich.normalize_affiliation(name), name)

        self.assertEqual(
            enrich.normalize_affiliation("The University of Queensland, Australia, {author}@uq.edu.au"),
            "The University of Queensland",
        )
        self.assertEqual(
            enrich.normalize_affiliation("University of Bari Aldo Moro, Bari, Italy"),
            "University of Bari Aldo Moro",
        )

    def test_company_names_are_not_classified_as_academic_institutions(self):
        for name in ("Meta", "LinkedIn", "ByteDance Seed", "Tencent", "Alibaba", "Huawei"):
            with self.subTest(name=name):
                self.assertEqual(enrich.institution_kind(name), "company")


if __name__ == "__main__":
    unittest.main()
