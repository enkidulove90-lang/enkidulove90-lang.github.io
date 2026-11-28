from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from notion_publish import NotionClient, markdown_to_blocks
from notion_sync import block_to_md


class EquationRoundTripTest(unittest.TestCase):
    def test_display_formula_round_trip_preserves_original_latex(self):
        latex = r"\frac{a}{b} + c"
        blocks = markdown_to_blocks("Before\n\n$$\n" + latex + "\n$$\n\nAfter")
        equations = [item for item in blocks if item["type"] == "equation"]
        self.assertEqual(equations, [{"object": "block", "type": "equation", "equation": {"expression": latex}}])
        self.assertEqual(block_to_md(equations[0]), "$$\n" + latex + "\n$$")

    def test_inline_formula_becomes_equation_rich_text_segment(self):
        blocks = markdown_to_blocks("Inline $x^2$ and text")
        self.assertEqual([item["type"] for item in blocks], ["paragraph"])
        rich = blocks[0]["paragraph"]["rich_text"]
        equations = [seg for seg in rich if seg.get("type") == "equation"]
        self.assertEqual(len(equations), 1)
        self.assertEqual(equations[0]["equation"]["expression"], "x^2")
        self.assertEqual("".join(
            s.get("text", {}).get("content", "") for s in rich if s.get("type") == "text"
        ), "Inline  and text")

    def test_inline_formula_round_trip_to_markdown(self):
        blocks = markdown_to_blocks("给定 $x_i$ 与 $y$，预测")
        # Simulate Notion read shape: equation segments carry equation.expression
        # plus a plain_text echo, exactly as the API returns them.
        read_segs = []
        for seg in blocks[0]["paragraph"]["rich_text"]:
            if seg.get("type") == "equation":
                expression = seg["equation"]["expression"]
                read_segs.append({"type": "equation", "equation": {"expression": expression},
                                  "plain_text": expression})
            else:
                read_segs.append({"plain_text": seg["text"]["content"]})
        rendered = block_to_md({"type": "paragraph", "paragraph": {"rich_text": read_segs}})
        self.assertEqual(rendered, "给定 $x_i$ 与 $y$，预测")

    def test_multiple_inline_formulas_on_one_line(self):
        blocks = markdown_to_blocks("$a$ then $b$ then $c$")
        rich = blocks[0]["paragraph"]["rich_text"]
        equations = [s["equation"]["expression"] for s in rich if s.get("type") == "equation"]
        self.assertEqual(equations, ["a", "b", "c"])

    def test_unclosed_display_formula_fails_before_any_loss(self):
        with self.assertRaisesRegex(ValueError, "unclosed"):
            markdown_to_blocks("Before\n$$\nx")

    def test_latex_linebreak_and_multiple_formulas_survive(self):
        latex = r"a \\ b"
        blocks = markdown_to_blocks("$$\n" + latex + "\n$$\n$$\nx\n$$")
        self.assertEqual([b["equation"]["expression"] for b in blocks], [latex, "x"])

    def test_equation_branch_edges_are_exercised(self):
        import dis
        import inspect
        import notion_publish
        import notion_sync
        if not hasattr(sys, "monitoring"):
            self.skipTest("branch monitoring requires Python 3.12+")
        functions = (notion_publish.markdown_to_blocks, notion_sync.block_to_md)
        targets = {func.__code__: func for func in functions}
        relevant = {}
        for code, function in targets.items():
            lines, first = inspect.getsourcelines(function)
            markers = (('if equation_lines is not None:', 'if line == "$$":', 'if not expression.strip():')
                       if function is notion_publish.markdown_to_blocks else ('elif t == "equation":',))
            relevant[code] = {first + index for index, text in enumerate(lines) if text.strip() in markers}
        expected, observed = set(), set()
        for code, function in targets.items():
            instructions = list(dis.get_instructions(function))
            for index, instruction in enumerate(instructions[:-1]):
                if instruction.opname.startswith("POP_JUMP") and instruction.positions.lineno in relevant[code]:
                    expected.update({(code.co_name, instruction.offset, instruction.argval),
                                     (code.co_name, instruction.offset, instructions[index + 1].offset)})
        def on_branch(code, offset, target):
            if code in targets:
                observed.add((code.co_name, offset, target))
        sys.monitoring.use_tool_id(5, "notion-equation-test")
        sys.monitoring.register_callback(5, sys.monitoring.events.BRANCH, on_branch)
        for code in targets:
            sys.monitoring.set_local_events(5, code, sys.monitoring.events.BRANCH)
        try:
            for text in ("plain", "$$\nx\n$$", "$$\n", "$$\n$$"):
                try:
                    notion_publish.markdown_to_blocks(text)
                except ValueError:
                    pass
            notion_sync.block_to_md({"type": "equation", "equation": {"expression": "x"}})
            notion_sync.block_to_md({"type": "bookmark", "bookmark": {"url": ""}})
        finally:
            for code in targets:
                sys.monitoring.set_local_events(5, code, 0)
            sys.monitoring.register_callback(5, sys.monitoring.events.BRANCH, None)
            sys.monitoring.free_tool_id(5)
        self.assertTrue(expected, "equation branch instrumentation did not find any conditional")
        self.assertFalse(expected - observed, f"uncovered equation branches: {sorted(expected - observed)}")


class MarkdownLinkRoundTripTest(unittest.TestCase):
    """[text](url) must become a clickable Notion link and survive sync back."""

    def test_inline_link_becomes_notion_link_rich_text(self):
        blocks = markdown_to_blocks("See [paper](https://arxiv.org/abs/2401.00001) for details.")
        rich = blocks[0]["paragraph"]["rich_text"]
        linked = [seg for seg in rich if seg.get("text", {}).get("link")]
        self.assertEqual(len(linked), 1)
        self.assertEqual(linked[0]["text"]["content"], "paper")
        self.assertEqual(linked[0]["text"]["link"]["url"], "https://arxiv.org/abs/2401.00001")

    def test_multiple_links_and_plain_text_coexist(self):
        blocks = markdown_to_blocks("[A](https://a.example) and [B](https://b.example) end")
        rich = blocks[0]["paragraph"]["rich_text"]
        links = [seg for seg in rich if seg.get("text", {}).get("link")]
        self.assertEqual([s["text"]["link"]["url"] for s in links],
                         ["https://a.example", "https://b.example"])
        self.assertTrue(any(" and " in seg.get("text", {}).get("content", "") for seg in rich))

    def test_reference_section_links_round_trip_to_markdown(self):
        md = "## References\n[1] [EchoMLLM](https://aclanthology.org/2026.findings-acl.1001/)"
        blocks = markdown_to_blocks(md)
        refs = next(b for b in blocks if b.get("type") == "paragraph")
        # Simulate Notion's read shape: it returns link as top-level href.
        read_segs = []
        for seg in refs["paragraph"]["rich_text"]:
            item = {"plain_text": seg["text"]["content"]}
            if seg.get("text", {}).get("link"):
                item["href"] = seg["text"]["link"]["url"]
            read_segs.append(item)
        rendered = "[1] " + block_to_md({"type": "paragraph", "paragraph": {"rich_text": read_segs}})
        self.assertIn("[EchoMLLM](https://aclanthology.org/2026.findings-acl.1001/)", rendered)

    def test_plain_url_is_not_mistaken_for_markdown_link(self):
        blocks = markdown_to_blocks("Visit https://example.org directly")
        rich = blocks[0]["paragraph"]["rich_text"]
        self.assertFalse(any(seg.get("text", {}).get("link") for seg in rich))

    def test_code_fence_keeps_markdown_link_as_literal_text(self):
        blocks = markdown_to_blocks("Example:\n\n```\n[label](https://example.org)\n```")
        codes = [b for b in blocks if b.get("type") == "code"]
        self.assertTrue(codes, blocks)
        text = "".join(seg.get("text", {}).get("content", "") for seg in codes[0]["code"]["rich_text"])
        self.assertIn("[label](https://example.org)", text)
        self.assertFalse(any(seg.get("text", {}).get("link") for seg in codes[0]["code"]["rich_text"]))

    def test_code_fence_keeps_inline_formula_literal(self):
        blocks = markdown_to_blocks("Code:\n\n```\nprice is $x_i$ here\n```")
        codes = [b for b in blocks if b.get("type") == "code"]
        self.assertTrue(codes, blocks)
        text = "".join(seg.get("text", {}).get("content", "") for seg in codes[0]["code"]["rich_text"])
        self.assertIn("$x_i$", text)
        self.assertFalse(any(seg.get("type") == "equation" for seg in codes[0]["code"]["rich_text"]))

    def test_escaped_dollar_is_not_treated_as_formula(self):
        blocks = markdown_to_blocks("Cost is \\$5 and $x$ is math")
        rich = blocks[0]["paragraph"]["rich_text"]
        equations = [s["equation"]["expression"] for s in rich if s.get("type") == "equation"]
        self.assertEqual(equations, ["x"])
        text = "".join(s.get("text", {}).get("content", "") for s in rich if s.get("type") == "text")
        self.assertIn("\\$5", text)


class MetadataPropertiesTest(unittest.TestCase):
    def setUp(self):
        self.client = NotionClient("test-token")
        self.values = {"venue_name": "ACL", "venue_type": "会议", "year": "2026",
                       "location_type": "affiliation", "venue_city": "Vienna",
                       "affil_city": ["Wuhan", "Beijing"], "corresponding_city": "Beijing",
                       "affiliation_name": "University"}

    def test_full_properties_use_default_types_and_multi_select(self):
        properties = self.client._properties(self.values)
        self.assertTrue(set(self.values) <= set(properties), properties)
        self.assertEqual(properties["affil_city"], {"multi_select": [{"name": "Wuhan"}, {"name": "Beijing"}]})
        self.assertEqual(properties["year"], {"select": {"name": "2026"}})
        self.assertEqual(properties["venue_name"]["rich_text"][0]["text"]["content"], "ACL")

    def test_partial_properties_do_not_add_empty_metadata(self):
        properties = self.client._properties({"venue_name": "ACL"})
        self.assertEqual(set(properties) & set(self.values), {"venue_name"})

    def test_missing_schema_property_is_warned(self):
        self.client._property_names = {"title", "slug", "status", "type"}
        with self.assertLogs("notion_publish", level="WARNING") as logs:
            properties = self.client._properties({"venue_name": "ACL"})
        self.assertNotIn("venue_name", properties)
        self.assertIn("venue_name", " ".join(logs.output))

    def test_schema_with_all_properties_encodes_declared_types(self):
        self.client._property_names = set(self.values) | {"title", "slug", "status", "type", "summary", "arxiv_id"}
        self.client._property_types = {"venue_name": "rich_text", "venue_type": "select", "year": "select",
            "location_type": "select", "venue_city": "rich_text", "affil_city": "multi_select",
            "corresponding_city": "select", "affiliation_name": "rich_text"}
        result = self.client._properties(self.values)
        self.assertTrue(set(self.values) <= set(result))
        self.assertEqual(result["location_type"], {"select": {"name": "affiliation"}})
        self.assertEqual(result["corresponding_city"], {"select": {"name": "Beijing"}})

    def test_incompatible_schema_type_rejected(self):
        self.client._property_names = {"affil_city"}
        self.client._property_types = {"affil_city": "rich_text"}
        with self.assertRaisesRegex(ValueError, "affil_city"):
            self.client._properties({"affil_city": ["Wuhan"]})

    def test_publication_fields_encode_against_live_types(self):
        self.client._property_names = {"title", "slug", "status", "type", "date", "category",
                                       "tags", "authors", "summary", "arxiv_id", "year"}
        self.client._property_types = {"date": "date", "category": "select", "tags": "multi_select",
                                       "authors": "rich_text", "summary": "rich_text",
                                       "arxiv_id": "rich_text", "year": "select"}
        result = self.client._properties({
            "date": "2026-10-04", "category": "推荐系统 / 多模态推荐",
            "tags": ["论文速读", "统一编码"], "authors": "Ada；Alan",
            "summary": "一句话摘要", "year": "2026"})
        self.assertEqual(result["date"], {"date": {"start": "2026-10-04"}})
        self.assertEqual(result["category"], {"select": {"name": "推荐系统 / 多模态推荐"}})
        self.assertEqual(result["tags"], {"multi_select": [{"name": "论文速读"}, {"name": "统一编码"}]})
        self.assertEqual(result["authors"]["rich_text"][0]["text"]["content"], "Ada；Alan")
        self.assertEqual(result["summary"]["rich_text"][0]["text"]["content"], "一句话摘要")
        self.assertEqual(result["year"], {"select": {"name": "2026"}})

    def test_date_is_dropped_when_schema_lacks_the_column(self):
        self.client._property_names = {"title", "slug"}
        result = self.client._properties({"date": "2026-10-04"})
        self.assertNotIn("date", result)

    def test_actual_schema_discovery_controls_property_types(self):
        class Transport:
            def request(self, method, path, **kwargs):
                if path == "/databases/db":
                    return {"data_sources": [{"id": "source"}]}
                if path == "/data_sources/source":
                    return {"properties": {"venue_name": {"type": "rich_text"},
                                           "venue_city": {"type": "select"},
                                           "affil_city": {"type": "multi_select"}}}
                return {"id": "page"}
        client = NotionClient("test-token", transport=Transport())
        client._data_source_id("db")
        result = client._properties({"venue_name": "ACL", "venue_city": "Vienna", "affil_city": ["Wuhan"]})
        self.assertEqual(result["venue_city"], {"select": {"name": "Vienna"}})
        self.assertEqual(result["affil_city"], {"multi_select": [{"name": "Wuhan"}]})

    def test_warns_if_schema_type_is_not_consumed_by_existing_sync(self):
        self.client._property_names = {"venue_name", "venue_type", "year"}
        self.client._property_types = {"venue_name": "select", "venue_type": "rich_text", "year": "rich_text"}
        with self.assertLogs("notion_publish", level="WARNING") as logs:
            result = self.client._properties({"venue_name": "ACL", "venue_type": "conference", "year": "2026"})
        self.assertEqual(result["venue_name"], {"select": {"name": "ACL"}})
        messages = " ".join(logs.output)
        for name in ("venue_name", "venue_type", "year"):
            self.assertIn(name, messages)


class LocationSchemaAlignmentTest(unittest.TestCase):
    """Five geography fields must encode against the REAL database schema (select)."""

    FIVE = ("location_type", "venue_city", "affil_city", "corresponding_city", "affiliation_name")

    def setUp(self):
        self.client = NotionClient("test-token")
        # Real schema discovered from the live database: four selects + one rich_text.
        self.client._property_names = set(self.FIVE) | {"title", "slug", "status", "type", "summary", "arxiv_id", "paper_key"}
        self.client._property_types = {
            "location_type": "select", "venue_city": "select", "affil_city": "select",
            "corresponding_city": "select", "affiliation_name": "rich_text",
        }

    def test_five_fields_encode_with_real_select_schema(self):
        values = {"location_type": "affiliation", "venue_city": "Vienna",
                  "affil_city": ["Wuhan"], "corresponding_city": "Wuhan",
                  "affiliation_name": "Wuhan University"}
        result = self.client._properties(values)
        for name in self.FIVE:
            self.assertIn(name, result, name)
        self.assertEqual(result["location_type"], {"select": {"name": "affiliation"}})
        self.assertEqual(result["venue_city"], {"select": {"name": "Vienna"}})
        self.assertEqual(result["affil_city"], {"select": {"name": "Wuhan"}})
        self.assertEqual(result["corresponding_city"], {"select": {"name": "Wuhan"}})
        self.assertEqual(result["affiliation_name"]["rich_text"][0]["text"]["content"], "Wuhan University")

    def test_affil_city_multi_value_on_select_schema_fails_loud(self):
        # select holds ONE option; two cities cannot be silently collapsed.
        with self.assertRaisesRegex(ValueError, "affil_city"):
            self.client._properties({"affil_city": ["Wuhan", "Beijing"]})

    def test_affil_city_accepts_scalar_string_on_select_schema(self):
        result = self.client._properties({"affil_city": "Wuhan"})
        self.assertEqual(result["affil_city"], {"select": {"name": "Wuhan"}})

    def test_sync_reads_back_five_fields_from_select_schema(self):
        from notion_sync import notion_location_fields
        props = {
            "location_type": {"select": {"name": "affiliation"}},
            "venue_city": {"select": {"name": "Vienna"}},
            "affil_city": {"select": {"name": "Wuhan"}},
            "corresponding_city": {"select": {"name": "Wuhan"}},
            "affiliation_name": {"rich_text": [{"plain_text": "Wuhan University"}]},
        }
        self.assertEqual(notion_location_fields(props), {
            "location_type": "affiliation", "venue_city": "Vienna",
            "affil_city": ["Wuhan"], "corresponding_city": "Wuhan",
            "affiliation_name": "Wuhan University",
        })


if __name__ == "__main__":
    unittest.main()
