"""Identity regressions and write precondition; no remote access."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from paper_article import ArticleDraft, validate_article
from paper_identity import canWriteSafely, detectIdentity, identityKey


class PaperIdentityTest(unittest.TestCase):
    def draft(self, **overrides):
        values = {"arxiv_id": "", "title": "EchoMLLM", "slug": "echo",
                  "markdown": "", "source_text": ""}
        values.update(overrides)
        return ArticleDraft(**values)

    def test_arxiv_modern_prefixed_url_and_legacy_formats(self):
        for fields in ({"arxiv_id": "2401.00001"}, {"arxiv_id": "arXiv:2401.00001"},
                       {"paper_url": "https://arxiv.org/abs/2401.00001"},
                       {"arxiv_id": "hep-th/9701001"}):
            with self.subTest(fields=fields):
                self.assertEqual(detectIdentity(self.draft(**fields))["type"], "arxiv")

    def test_echo_identity_is_acl(self):
        draft = self.draft(doi="10.18653/v1/2026.findings-acl.1001")
        self.assertEqual(detectIdentity(draft), {"type": "acl_doi", "canonicalId": draft.doi})

    def test_echo_validation_does_not_report_missing_identity(self):
        draft = self.draft(doi="10.18653/v1/2026.findings-acl.1001")
        self.assertNotIn("missing recognized paper identity", validate_article(draft))

    def test_both_identifiers_are_preserved(self):
        draft = self.draft(arxiv_id="2401.00001", doi="10.18653/v1/2026.findings-acl.1001")
        self.assertEqual(detectIdentity(draft)["type"], "both")

    def test_acl_doi_forms_and_invalid_doi(self):
        for value in ("10.18653/v1/2026.findings-acl.1001",
                      "https://doi.org/10.18653/v1/2026.findings-acl.1001",
                      "https://aclanthology.org/2026.findings-acl.1001/"):
            with self.subTest(value=value):
                self.assertEqual(detectIdentity(self.draft(paper_url=value))["type"], "acl_doi")
        self.assertEqual(detectIdentity(self.draft(doi="10.18653/fake"))["type"], "none")

    def test_write_guard_uses_valid_arxiv_id_not_acl_or_url_alone(self):
        from paper_identity import needs_arxiv_for_write
        for draft, expected in (
            (self.draft(doi="10.18653/v1/2026.findings-acl.1001"), True),
            (self.draft(arxiv_id=""), True),
            (self.draft(arxiv_id="bad"), True),
            (self.draft(paper_url="https://arxiv.org/abs/2401.00001"), True),
            (self.draft(arxiv_id="2401.00001"), False),
            (self.draft(arxiv_id="2401.00001", doi="10.18653/v1/2026.findings-acl.1001"), False),
        ):
            with self.subTest(draft=draft):
                self.assertEqual(needs_arxiv_for_write(draft), expected)

    def test_detect_identity_all_conditional_branches(self):
        import dis
        if not hasattr(sys, "monitoring"):
            self.skipTest("runtime branch monitoring requires Python 3.12+")
        instructions = list(dis.get_instructions(detectIdentity))
        offsets = [instruction.offset for instruction in instructions]
        expected = set()
        for index, item in enumerate(instructions[:-1]):
            if not (item.opname.startswith("POP_JUMP") or item.opname == "FOR_ITER"):
                continue
            target = item.argval
            if item.opname == "FOR_ITER" and instructions[offsets.index(target)].opname == "END_FOR":
                position = offsets.index(target) + 1
                if instructions[position].opname == "POP_TOP":
                    position += 1
                target = offsets[position]
            expected.update({(item.offset, target), (item.offset, instructions[index + 1].offset)})
        observed = set()
        tool_id = 5
        def on_branch(code, offset, target):
            if code is detectIdentity.__code__:
                observed.add((offset, target))
        samples = [
            {}, {"arxiv_id": "2401.00001"},
            {"arxiv_id": "2401.00001", "paper_url": "https://arxiv.org/abs/2401.00001"},
            {"arxiv_id": "2401.00001", "doi": "10.18653/v1/2026.findings-acl.1001"},
            {"doi": "10.18653/v1/2026.findings-acl.1001", "paper_url": "https://aclanthology.org/2026.findings-acl.1001/"},
            {"doi": "10.18653/v1/fake"}, {"doi": "10.18653/fake"},
            {"paper_url": "https://doi.org/10.18653/v1/2026.findings-acl.1001"},
            {"paper_url": "https://arxiv.org/abs/2401.00001"}, {"paper_url": "https://arxiv.org/other/2401.00001"},
            {"paper_url": "https://invalid.example/paper"}, {"paper_url": "ftp://arxiv.org/abs/2401.00001"},
            {"paper_url": "https://user@arxiv.org/abs/2401.00001"},
            {"paper_url": "https://:secret@arxiv.org/abs/2401.00001"}, {"paper_url": "https:///abs/2401.00001"},
        ]
        sys.monitoring.use_tool_id(tool_id, "paper-identity-test")
        sys.monitoring.register_callback(tool_id, sys.monitoring.events.BRANCH, on_branch)
        sys.monitoring.set_local_events(tool_id, detectIdentity.__code__, sys.monitoring.events.BRANCH)
        try:
            for raw in samples:
                detectIdentity(raw)
        finally:
            sys.monitoring.set_local_events(tool_id, detectIdentity.__code__, 0)
            sys.monitoring.register_callback(tool_id, sys.monitoring.events.BRANCH, None)
            sys.monitoring.free_tool_id(tool_id)
        self.assertFalse(expected - observed,
                         f"uncovered conditional branch edges: {sorted(expected - observed)}")


class IdentityKeyTest(unittest.TestCase):
    """P0: one stable key drives dedup, path and receipt across id forms."""

    def draft(self, **overrides):
        values = {"arxiv_id": "", "title": "EchoMLLM", "slug": "echo",
                  "markdown": "", "source_text": ""}
        values.update(overrides)
        return ArticleDraft(**values)

    def test_identity_key_arxiv_strips_version(self):
        self.assertEqual(identityKey(self.draft(arxiv_id="2401.00001v3")), "2401.00001")

    def test_identity_key_acl_doi_is_filesystem_safe(self):
        key = identityKey(self.draft(doi="10.18653/v1/2026.findings-acl.1001"))
        self.assertEqual(key, "acl-2026-findings-acl-1001")
        self.assertNotIn("/", key)
        self.assertNotIn(".", key)

    def test_identity_key_acl_url_forms_are_stable(self):
        keys = {
            identityKey(self.draft(paper_url=value))
            for value in (
                "https://doi.org/10.18653/v1/2026.findings-acl.1001",
                "https://aclanthology.org/2026.findings-acl.1001/",
                "10.18653/v1/2026.findings-acl.1001",
            )
        }
        self.assertEqual(len(keys), 1)
        self.assertEqual(next(iter(keys)), "acl-2026-findings-acl-1001")

    def test_identity_key_both_prefers_arxiv(self):
        draft = self.draft(arxiv_id="2401.00001", doi="10.18653/v1/2026.findings-acl.1001")
        self.assertEqual(identityKey(draft), "2401.00001")

    def test_identity_key_none_is_empty(self):
        self.assertEqual(identityKey(self.draft()), "")

    def test_can_write_safely_matches_nonempty_key(self):
        cases = (
            (self.draft(arxiv_id="2401.00001"), True),
            (self.draft(doi="10.18653/v1/2026.findings-acl.1001"), True),
            (self.draft(), False),
        )
        for draft, expected in cases:
            with self.subTest(draft=draft):
                self.assertEqual(canWriteSafely(draft), expected)
                self.assertEqual(canWriteSafely(draft), bool(identityKey(draft)))


if __name__ == "__main__":
    unittest.main()
