from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))


def sample():
    return {"article_input": {"title": "Paper", "slug": "paper-1", "markdown": "# Paper",
        "arxiv_id": "2401.00001", "source_text": "evidence",
        "figures": [{"path": "fig.png", "caption": "caption", "dimensions": [1280, 720],
                     "is_hd": True, "provenance": "mineru", "page_number": 2}],
        "source_pdf": "paper.pdf", "source_spans": {"method": "p1"},
        "doi": "10.18653/v1/2026.findings-acl.1001", "canonical_id": "arxiv:2401.00001",
        "paper_url": "https://arxiv.org/abs/2401.00001"},
        "facts": {"authors": [{"name": "A"}], "venue_name": "ACL", "verification_status": "verified"},
        "references": [{"title": "Prior", "verification_status": "verified"}],
        "location": {"venue_city": "Vienna", "verification_status": "verified"},
        "formulae": [{"latex": "x^2", "display_mode": "block", "source_location": "p1"}],
        "identity_status": "ready", "blog_compatibility": "not_validated", "review_status": "pending",
        "missing_fields": ["other"]}


class ReviewAdapterTest(unittest.TestCase):
    def test_visual_review_status_flows_from_manifest(self):
        from review_adapter import adapt
        raw = sample()
        raw["article_input"]["figures"][0]["visual_review"] = "reviewed: caption matches Figure 1"
        raw["article_input"]["figures"][0]["manifest_sha256"] = "abc123"
        draft = adapt(raw)
        figure = draft.figures[0]
        self.assertEqual(figure.visual_review, "reviewed: caption matches Figure 1")
        self.assertEqual(figure.manifest_sha256, "abc123")

    def test_missing_visual_review_defaults_to_empty(self):
        from review_adapter import adapt
        draft = adapt(sample())
        self.assertEqual(draft.figures[0].visual_review, "")

    def test_maps_all_fields_and_figures_without_modifying_input(self):
        from review_adapter import adapt
        from unittest.mock import patch
        raw = sample()
        before = copy.deepcopy(raw)
        draft = adapt(raw)
        self.assertEqual((draft.title, draft.slug, draft.markdown), ("Paper", "paper-1", "# Paper"))
        self.assertEqual((draft.arxiv_id, draft.source_text, draft.doi, draft.canonical_id, draft.paper_url),
            ("2401.00001", "evidence", "10.18653/v1/2026.findings-acl.1001", "arxiv:2401.00001", "https://arxiv.org/abs/2401.00001"))
        self.assertEqual(draft.source_pdf, Path("paper.pdf"))
        self.assertEqual(draft.source_spans, {"method": "p1"})
        figure = draft.figures[0]
        self.assertEqual((figure.path, figure.caption, figure.dimensions, figure.is_hd, figure.provenance, figure.page_number),
                         (Path("fig.png"), "caption", (1280, 720), True, "mineru", 2))
        self.assertEqual(raw, before)
        self.assertEqual(adapt(raw), draft)
        with patch("pathlib.Path.read_text", side_effect=AssertionError("file read in adapt")), \
             patch("socket.create_connection", side_effect=AssertionError("network in adapt")):
            self.assertEqual(adapt(raw), draft)

    def test_missing_required_fields_report_json_path(self):
        from review_adapter import adapt, AdapterError
        for key in ("title", "slug", "markdown"):
            with self.subTest(key=key):
                raw = sample()
                del raw["article_input"][key]
                with self.assertRaisesRegex(AdapterError, r"\$\.article_input\." + key):
                    adapt(raw)

    def test_empty_values_and_optional_defaults(self):
        from review_adapter import adapt
        raw = {"article_input": {"title": "T", "slug": "S", "markdown": "", "arxiv_id": None,
                                 "figures": [], "source_pdf": None}, "page": {}, "blocks": []}
        draft = adapt(raw)
        self.assertEqual((draft.markdown, draft.arxiv_id, draft.source_text, draft.figures, draft.source_pdf),
                         ("", "", "", [], None))
        self.assertEqual((draft.source_spans, draft.doi, draft.canonical_id, draft.paper_url), ({}, "", "", ""))

    def test_arxiv_id_missing_defaults_to_empty(self):
        from review_adapter import adapt
        raw = {"article_input": {"title": "T", "slug": "S", "markdown": ""}}
        self.assertEqual(adapt(raw).arxiv_id, "")

    def test_empty_reference_list_is_present_but_empty(self):
        from review_adapter import adapt_metadata
        metadata = adapt_metadata({"references": []})
        self.assertEqual(metadata.references.status, "present_but_empty")
        self.assertEqual(metadata.references.value, [])

    def test_bad_figures_are_rejected_with_path(self):
        from review_adapter import adapt, AdapterError
        raw = sample()
        del raw["article_input"]["figures"][0]["path"]
        with self.assertRaisesRegex(AdapterError, r"\$\.article_input\.figures\[0\]\.path"):
            adapt(raw)

    def test_metadata_states_and_statuses_preserve_uncertainty(self):
        from review_adapter import adapt_metadata
        raw = sample()
        metadata = adapt_metadata(raw)
        self.assertEqual(metadata.authors.status, "present")
        self.assertEqual(metadata.venue.status, "present")
        self.assertEqual(metadata.references.status, "present")
        self.assertEqual(metadata.location.status, "present")
        self.assertEqual(metadata.formulae.status, "pending_verification")
        self.assertEqual(metadata.formulae.value[0]["display_mode"], "block")
        self.assertEqual((metadata.identity_status, metadata.blog_compatibility, metadata.review_status, metadata.missing_fields),
                         ("ready", "not_validated", "pending", ["other"]))
        raw["location"] = None
        raw["formulae"] = []
        raw["facts"]["verification_status"] = "unverified"
        metadata = adapt_metadata(raw)
        self.assertEqual(metadata.location.status, "missing")
        self.assertEqual(metadata.formulae.status, "present_but_empty")
        self.assertEqual(metadata.authors.status, "pending_verification")
        self.assertEqual(adapt_metadata({}).authors.status, "missing")

    def test_load_review_only_reads_json(self):
        from review_adapter import load_review
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notion.json"
            path.write_text(json.dumps(sample()), encoding="utf-8")
            self.assertEqual(load_review(path), sample())

    def test_actual_echo_review_asset_when_available(self):
        from review_adapter import adapt, adapt_metadata, load_review
        path = Path("D:/recommendation-system-learning/data/blog_identity_tests_n/test_real_echomllm_assets_comp0/publish_queue/notion/4840fb51235a06ee8238ae1f792fb59e/notion.json")
        try:
            available = path.is_file()
        except PermissionError:
            available = False
        if not available:
            self.skipTest("optional EchoMLLM local review package unavailable")
        raw = load_review(path)
        draft = adapt(raw)
        metadata = adapt_metadata(raw)
        self.assertEqual(draft.canonical_id, "2026.findings-acl.1001")
        self.assertEqual(len(draft.figures), 9)
        self.assertEqual(metadata.location.status, "missing")
        self.assertEqual(metadata.formulae.status, "present_but_empty")
        self.assertEqual(metadata.review_status, "pending")

    def test_invalid_inputs_and_unverified_metadata_are_explicit(self):
        from review_adapter import adapt, adapt_metadata, AdapterError
        for field, bad in (("figures", None), ("source_spans", []), ("source_spans", {"x": 1}),
                           ("source_pdf", ""), ("arxiv_id", 123)):
            raw = sample()
            raw["article_input"][field] = bad
            with self.subTest(field=field, bad=bad), self.assertRaisesRegex(AdapterError, r"\$\.article_input\." + field):
                adapt(raw)
        for path, raw in (("$.facts.authors", {"facts": {"authors": "bad"}}),
                          ("$.references", {"references": "bad"}),
                          ("$.formulae", {"formulae": "bad"}),
                          ("$.facts.venue_name", {"facts": {"venue_name": 4}}),
                          ("$.location", {"location": "bad"})):
            with self.subTest(path=path), self.assertRaises(AdapterError) as error:
                adapt_metadata(raw)
            self.assertIn(path, str(error.exception))
        metadata = adapt_metadata({"facts": {"authors": [], "venue_name": "ACL"},
                                   "references": [{"title": "Prior"}], "location": {"venue_city": "Vienna"},
                                   "formulae": []})
        self.assertEqual(metadata.authors.status, "present_but_empty")
        self.assertEqual(metadata.venue.status, "pending_verification")
        self.assertEqual(metadata.references.status, "pending_verification")
        self.assertEqual(metadata.location.status, "pending_verification")

    def test_adapt_functions_conditional_branch_coverage(self):
        """Exercise both successors of every conditional bytecode in the two functions."""
        import dis
        from review_adapter import adapt, adapt_metadata, AdapterError
        targets = {func.__code__: func for func in (adapt, adapt_metadata)}
        expected, observed = set(), set()
        for code, func in targets.items():
            instructions = list(dis.get_instructions(func))
            offsets = [item.offset for item in instructions]
            for index, item in enumerate(instructions[:-1]):
                if not (item.opname.startswith("POP_JUMP") or item.opname == "FOR_ITER"):
                    continue
                destination = item.argval
                if item.opname == "FOR_ITER" and instructions[offsets.index(destination)].opname == "END_FOR":
                    pos = offsets.index(destination) + 1
                    if instructions[pos].opname == "POP_TOP":
                        pos += 1
                    destination = offsets[pos]
                expected.update({(code.co_name, item.offset, destination),
                                 (code.co_name, item.offset, instructions[index + 1].offset)})

        if not hasattr(sys, "monitoring"):
            self.skipTest("branch monitoring requires Python 3.12 or later")
        tool_id = 5
        def tracer(code, offset, destination):
            if code in targets:
                observed.add((code.co_name, offset, destination))

        base = {"article_input": {"title": "T", "slug": "S", "markdown": ""}}
        cases = [(adapt, base), (adapt, sample()),
                 (adapt, {"article_input": {**base["article_input"], "figures": "bad"}}),
                 (adapt, {"article_input": {**base["article_input"], "source_spans": []}}),
                 (adapt, {"article_input": {**base["article_input"], "source_spans": {"k": 1}}}),
                 (adapt_metadata, {}), (adapt_metadata, sample()),
                 (adapt_metadata, {"facts": {"authors": "bad"}}),
                 (adapt_metadata, {"references": "bad"}),
                 (adapt_metadata, {"facts": {"venue_name": 5}}),
                 (adapt, {**sample(), "references": "bad"}),
                 (adapt, {**sample(), "references": [{"title": "ok"}, "not-a-dict"]}),
                 (adapt, {**sample(), "fact_provenance": "bad"}),
                 (adapt, {**sample(), "fact_provenance": {"fields": {}}}),
                 (adapt, {**sample(), "fact_provenance": {"fields": {
                     "paper_title": {"verification_status": "verified"}}}}),
                 (adapt_metadata, {**sample(), "fact_provenance": {"fields": {}}})]
        sys.monitoring.use_tool_id(tool_id, "review-adapter-test")
        sys.monitoring.register_callback(tool_id, sys.monitoring.events.BRANCH, tracer)
        for code in targets:
            sys.monitoring.set_local_events(tool_id, code, sys.monitoring.events.BRANCH)
        try:
            for function, raw in cases:
                try:
                    function(raw)
                except AdapterError:
                    pass
        finally:
            for code in targets:
                sys.monitoring.set_local_events(tool_id, code, 0)
            sys.monitoring.register_callback(tool_id, sys.monitoring.events.BRANCH, None)
            sys.monitoring.free_tool_id(tool_id)
        missing = expected - observed
        self.assertFalse(missing, f"missed conditional branches: {sorted(missing)}; "
                         f"observed for those origins: {sorted(edge for edge in observed if (edge[0], edge[1]) in {(x[0], x[1]) for x in missing})}")


if __name__ == "__main__":
    unittest.main()
