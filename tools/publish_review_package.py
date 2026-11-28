#!/usr/bin/env python3
"""Inspect a review package offline, or explicitly deliver via the existing publisher."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from notion_publish import NotionClient, publish_article
from paper_article import check_article, validate_article
from paper_identity import detectIdentity, identityKey
from review_adapter import adapt, adapt_metadata, load_review


def _publication_metadata(raw: dict, metadata) -> dict:
    """Shape the review package's fields for Notion property types.

    Publication date, authors, summary, year, category and tags are written so
    ``notion_sync`` never falls back to the page creation time, and so the
    homepage filters (year / venue / tags) have something to filter on. Venue
    name and type only go in when the venue passed verification — an
    unverified venue would otherwise overwrite a correct classification.
    """
    facts = raw.get("facts") or {}
    if not isinstance(facts, dict):
        return {}
    homepage = raw.get("homepage_draft") or {}
    values: dict = {}

    published = str(facts.get("published_date") or "").strip()
    if published:
        values["date"] = published[:10]

    authors = facts.get("authors") or []
    names = [str(item.get("name") or "").strip() for item in authors if isinstance(item, dict)]
    names = [name for name in names if name]
    if names:
        values["authors"] = "；".join(names)[:1900]

    summary = str(homepage.get("summary_1line") or facts.get("one_line") or "").strip()
    if summary:
        values["summary"] = summary[:1900]

    year = str(facts.get("year") or "").strip()
    if year:
        values["year"] = year

    if metadata.venue.status == "present":
        venue_name = str(facts.get("venue_name") or "").strip()
        venue_type = str(facts.get("venue_type") or "").strip()
        if venue_name:
            values["venue_name"] = venue_name
        if venue_type:
            values["venue_type"] = venue_type

    categories = facts.get("categories") or facts.get("category") or []
    if isinstance(categories, str):
        categories = [part.strip() for part in categories.replace("、", "/").split("/") if part.strip()]
    categories = [str(item).strip() for item in categories if str(item).strip()]
    if categories:
        values["category"] = " / ".join(categories[:2])

    keywords = facts.get("keywords") or []
    tags = [str(item).strip() for item in keywords if str(item).strip()]
    if tags:
        values["tags"] = tags[:8]

    return values


def _single_city_location(location: dict) -> tuple[dict, list]:
    """Reduce a multi-city affiliation to the one city a Select column can hold.

    The live database stores affil_city as a Select, so exactly one city is
    writable. Keep the corresponding author's city when it is one of the
    affiliation cities, and return the rest so the report can name them.
    """
    cities = location.get("affil_city")
    if not isinstance(cities, list) or len(cities) <= 1:
        return location, []
    cities = [city for city in cities if isinstance(city, str) and city]
    if not cities:
        return {**location, "affil_city": []}, []
    corresponding = str(location.get("corresponding_city") or "").strip()
    keep = corresponding if corresponding in cities else cities[0]
    reduced = {**location, "affil_city": [keep]}
    if not corresponding:
        reduced["corresponding_city"] = keep
    return reduced, [city for city in cities if city != keep]


def run_review_package(review_json: Path, *, write_notion: bool = False,
                       database_id: str = "", token: str = "", client=None,
                       allow_overwrite: bool = False, skip_if_exists: bool = True,
                       promote: bool = True):
    """Return (ArticleDraft, AdapterMetadata, report). Default mode never uses network.

    ``skip_if_exists`` defaults True: if the paper already has a Notion page
    (matched by identity key), report ``already_exists`` and skip — never
    overwrite an existing article. Pass False with ``allow_overwrite=True`` to
    force a replace.

    ``promote`` defaults True (user decision 2026-11-28): running the publish
    command publishes straight to the homepage (status=Published). Pass
    ``promote=False`` (CLI ``--draft``) to keep it Invisible as a draft.
    """
    raw = load_review(review_json)
    draft = adapt(raw)
    metadata = adapt_metadata(raw)
    # Notion is a draft sink: only truth gaps block, presentation defects
    # (non-HD figures, missing captions) are advisory. This applies to both
    # dry-run and write so "fields present → upload" holds end to end.
    gate_stage = "draft"
    errors, warnings = check_article(draft, stage=gate_stage)
    identity = detectIdentity(draft)
    sources = [name for name in ("arxiv_id", "doi", "canonical_id", "paper_url")
               if detectIdentity({name: getattr(draft, name)})["type"] != "none"]
    report = {
        "mode": "write" if write_notion else "dry_run",
        "article": {"title": draft.title, "slug": draft.slug, "arxiv_id": draft.arxiv_id,
                    "doi": draft.doi, "canonical_id": draft.canonical_id, "paper_url": draft.paper_url,
                    "markdown_chars": len(draft.markdown), "source_text_chars": len(draft.source_text),
                    "figure_count": len(draft.figures),
                    "source_pdf": str(draft.source_pdf) if draft.source_pdf is not None else None,
                    "source_spans": dict(draft.source_spans)},
        "metadata_status": {name: getattr(metadata, name).status
                            for name in ("authors", "venue", "references", "location", "formulae")},
        "publication_metadata": _publication_metadata(raw, metadata),
        "identity": {**identity, "sources": sources, "identity_key": identityKey(draft)},
        "gate_stage": gate_stage,
        "errors": errors,
        "warnings": warnings,
        "delivery": None,
    }
    if write_notion:
        # The single write gate lives in publish_article(); no local duplicate.
        if errors:
            raise ValueError("article validation failed: " + "; ".join(errors))
        if not database_id:
            raise ValueError("NOTION_DATABASE_ID is required for write mode")
        if client is None:
            client = NotionClient(token)
        # Only verified location (status == "present") is written; pending/missing
        # metadata never reaches Notion.
        publisher_kwargs = {"write": True, "promote": promote,
                            "allow_overwrite": allow_overwrite,
                            "skip_if_exists": skip_if_exists,
                            "gate_stage": gate_stage,
                            "metadata": _publication_metadata(raw, metadata)}
        if metadata.location.status == "present" and isinstance(metadata.location.value, dict):
            location_value, dropped = _single_city_location(metadata.location.value)
            publisher_kwargs["location"] = location_value
            if dropped:
                # The live column is a Select (one city). Say which affiliation
                # cities were not written instead of collapsing them silently.
                report["dropped_affil_cities"] = dropped
        result = publish_article(client, draft, database_id, **publisher_kwargs)
        report["delivery"] = {"action": result.action, "page_id": result.page_id,
                              "status": result.status, "identity_key": result.identity_key,
                              "overwrite_snapshot": result.overwrite_snapshot}
    return draft, metadata, report


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a local review package; write only when explicitly requested")
    parser.add_argument("--review-json", type=Path, required=True)
    parser.add_argument("--write-notion", action="store_true")
    parser.add_argument("--allow-overwrite", action="store_true",
                        help="Explicitly clear and replace an existing non-empty page body")
    parser.add_argument("--draft", action="store_true",
                        help="Keep the Notion page Invisible (default publishes to homepage)")
    args = parser.parse_args()
    _, _, report = run_review_package(args.review_json, write_notion=args.write_notion,
        database_id=os.environ.get("NOTION_DATABASE_ID", "") if args.write_notion else "",
        token=os.environ.get("NOTION_TOKEN", "") if args.write_notion else "",
        allow_overwrite=args.allow_overwrite,
        skip_if_exists=not args.allow_overwrite,
        promote=not args.draft)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
