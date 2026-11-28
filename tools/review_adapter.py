"""Convert a local notion-review/v1 package without performing I/O in adapt().

Consumed paths: $.article_input.{title,slug,markdown,arxiv_id,source_text,
figures,source_pdf,source_spans,doi,canonical_id,paper_url};
$.facts.{authors,venue_name,verification_status}; $.references, $.location,
$.formulae, $.identity_status, $.blog_compatibility, $.review_status,
$.missing_fields. Unknown paths are ignored.

ArticleDraft mapping: title/slug/markdown/arxiv_id/source_text/source_spans/
doi/canonical_id/paper_url <- same-named article_input fields; source_pdf <-
Path or None; figures[*] <- FigureAsset(path,caption,dimensions,is_hd,
provenance,page_number). Other fields are exposed only via adapt_metadata().
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mineru_adapter import FigureAsset
from paper_article import ArticleDraft


class AdapterError(ValueError):
    """An invalid or missing review-package value with its JSON path."""


@dataclass(frozen=True)
class MetadataValue:
    status: str
    value: Any = None


@dataclass(frozen=True)
class AdapterMetadata:
    authors: MetadataValue
    venue: MetadataValue
    references: MetadataValue
    location: MetadataValue
    formulae: MetadataValue
    fact_provenance: MetadataValue
    identity_status: Any
    blog_compatibility: Any
    review_status: Any
    missing_fields: Any


def load_review(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _object(value: Any, path: str) -> dict:
    if not isinstance(value, dict):
        raise AdapterError(f"{path}: expected object")
    return value


def _string(value: Any, path: str, *, allow_empty: bool = True) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise AdapterError(f"{path}: expected {'string' if allow_empty else 'non-empty string'}")
    return value


def _optional_string(data: dict, key: str) -> str:
    value = data.get(key)
    if value is None:
        return ""
    return _string(value, f"$.article_input.{key}")


def _figure(raw: Any, index: int) -> FigureAsset:
    base = f"$.article_input.figures[{index}]"
    data = _object(raw, base)
    path = _string(data.get("path"), base + ".path", allow_empty=False)
    caption = _string(data.get("caption"), base + ".caption")
    provenance = _string(data.get("provenance"), base + ".provenance")
    dimensions = data.get("dimensions")
    if not isinstance(dimensions, (list, tuple)) or len(dimensions) != 2 or any(
        not isinstance(n, int) or isinstance(n, bool) or n <= 0 for n in dimensions
    ):
        raise AdapterError(base + ".dimensions: expected two positive integers")
    is_hd = data.get("is_hd")
    if not isinstance(is_hd, bool):
        raise AdapterError(base + ".is_hd: expected boolean")
    page = data.get("page_number")
    if page is not None and (not isinstance(page, int) or isinstance(page, bool) or page < 1):
        raise AdapterError(base + ".page_number: expected positive integer or null")
    raw_visual = data.get("visual_review", "")
    raw_hash = data.get("manifest_sha256", "")
    visual_review = raw_visual if isinstance(raw_visual, str) else ""
    manifest_sha256 = raw_hash if isinstance(raw_hash, str) else ""
    return FigureAsset(path=Path(path), caption=caption, dimensions=tuple(dimensions),
                       is_hd=is_hd, provenance=provenance, page_number=page,
                       visual_review=visual_review, manifest_sha256=manifest_sha256)


def adapt(raw: dict) -> ArticleDraft:
    root = _object(raw, "$")
    data = _object(root.get("article_input"), "$.article_input")
    title = _string(data.get("title"), "$.article_input.title", allow_empty=False)
    slug = _string(data.get("slug"), "$.article_input.slug", allow_empty=False)
    markdown = _string(data.get("markdown"), "$.article_input.markdown")
    raw_figures = data.get("figures", [])
    if not isinstance(raw_figures, list):
        raise AdapterError("$.article_input.figures: expected array")
    spans = data.get("source_spans", {})
    if not isinstance(spans, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in spans.items()):
        raise AdapterError("$.article_input.source_spans: expected string-to-string object")
    raw_pdf = data.get("source_pdf")
    pdf = None if raw_pdf is None else Path(_string(raw_pdf, "$.article_input.source_pdf", allow_empty=False))
    raw_refs = root.get("references", [])
    if not isinstance(raw_refs, list):
        raise AdapterError("$.references: expected array")
    refs = [copy.deepcopy(item) for item in raw_refs if isinstance(item, dict)]
    raw_prov = root.get("fact_provenance")
    if raw_prov is not None and not isinstance(raw_prov, dict):
        raise AdapterError("$.fact_provenance: expected object")
    return ArticleDraft(arxiv_id=_optional_string(data, "arxiv_id"), title=title, slug=slug,
        markdown=markdown, source_text=_optional_string(data, "source_text"),
        figures=[_figure(figure, i) for i, figure in enumerate(raw_figures)], source_pdf=pdf,
        source_spans=dict(spans), doi=_optional_string(data, "doi"),
        canonical_id=_optional_string(data, "canonical_id"), paper_url=_optional_string(data, "paper_url"),
        references=refs, fact_provenance=copy.deepcopy(raw_prov) if raw_prov else None)


def _metadata_value(value: Any, verified: bool = False) -> MetadataValue:
    if value is None or value == "":
        return MetadataValue("missing")
    if isinstance(value, (list, dict)) and not value:
        return MetadataValue("present_but_empty", copy.deepcopy(value))
    return MetadataValue("present" if verified else "pending_verification", copy.deepcopy(value))


def _records_verified(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, dict) and item.get("verification_status") == "verified" for item in value)


def adapt_metadata(raw: dict) -> AdapterMetadata:
    root = _object(raw, "$")
    facts = _object(root.get("facts", {}), "$.facts")
    location = root.get("location")
    if location is not None:
        location = _object(location, "$.location")
    references = root.get("references")
    formulae = root.get("formulae")
    for name, value in (("authors", facts.get("authors")), ("references", references), ("formulae", formulae)):
        if value is not None and not isinstance(value, list):
            raise AdapterError(f"$.{'facts.' if name == 'authors' else ''}{name}: expected array or null")
    if facts.get("venue_name") is not None and not isinstance(facts["venue_name"], str):
        raise AdapterError("$.facts.venue_name: expected string or null")
    verified = facts.get("verification_status") == "verified"
    return AdapterMetadata(
        authors=_metadata_value(facts.get("authors"), verified),
        venue=_metadata_value(facts.get("venue_name"), verified),
        references=_metadata_value(references, _records_verified(references)),
        # A location is publishable when the city is header-verified OR derived
        # from the institution by the model ("inferred"). The two stay distinct
        # in the payload so the site can label an inferred pin.
        location=_metadata_value(location, bool(
            location and location.get("verification_status") in {"verified", "inferred"})),
        formulae=_metadata_value(formulae, _records_verified(formulae)),
        fact_provenance=_metadata_value(root.get("fact_provenance"), True),
        identity_status=copy.deepcopy(root.get("identity_status")),
        blog_compatibility=copy.deepcopy(root.get("blog_compatibility")),
        review_status=copy.deepcopy(root.get("review_status")),
        missing_fields=copy.deepcopy(root.get("missing_fields")))
