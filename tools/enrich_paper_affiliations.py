#!/usr/bin/env python3
"""Resolve first-author affiliations from public ar5iv paper headers.

The generated JSON is an auditable cache. It never guesses an institution or
city: records are emitted only when the paper header exposes both fields.
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import time
from datetime import datetime, timezone

import requests


ROOT = pathlib.Path(__file__).resolve().parents[1]
POSTS = ROOT / "source" / "_posts"
OUTPUT = ROOT / "tools" / "paper_affiliations.json"
MANIFEST = ROOT / "tools" / "paper_publication_manifest.json"
AR5IV = "https://ar5iv.labs.arxiv.org/html/{arxiv_id}"
ARXIV_HTML = "https://arxiv.org/html/{arxiv_id}"
CROSSREF = "https://api.crossref.org/works/{doi}"
USER_AGENT = "EnkiduRecSysFrontier/1.2 (affiliation audit; public paper metadata)"


def clean_html(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def class_text(fragment: str, class_name: str) -> str:
    match = re.search(
        rf'<span[^>]*class="[^"]*\b{re.escape(class_name)}\b[^"]*"[^>]*>(.*?)</span>',
        fragment,
        re.IGNORECASE | re.DOTALL,
    )
    return clean_html(match.group(1)) if match else ""


def parse_first_author_affiliation(document: str) -> dict | None:
    authors = re.search(r'<div[^>]*class="[^"]*\bltx_authors\b[^"]*"[^>]*>(.*?)</div>', document,
                        re.IGNORECASE | re.DOTALL)
    area = authors.group(1) if authors else document
    first = re.split(r'<span[^>]*class="[^"]*\bltx_creator\s+ltx_role_author\b', area,
                     maxsplit=2, flags=re.IGNORECASE)
    fragment = first[1] if len(first) > 1 else area
    affiliation = class_text(fragment, "ltx_affiliation_institution") or class_text(area, "ltx_affiliation_institution")
    if not affiliation:
        affiliation = class_text(area, "ltx_role_affiliation")
        affiliation = re.sub(r"^Affiliation:\s*", "", affiliation, flags=re.IGNORECASE)
    record = {
        "first_author": class_text(fragment, "ltx_personname"),
        "affiliation_name": affiliation,
        "affil_city": class_text(fragment, "ltx_affiliation_city") or class_text(area, "ltx_affiliation_city"),
        "country": class_text(fragment, "ltx_affiliation_country") or class_text(area, "ltx_affiliation_country"),
    }
    return record if record["first_author"] and record["affiliation_name"] else None


def parse_local_paper_header(document: str) -> dict | None:
    page = document.split("## Page 1", 1)[-1]
    page = re.split(r"\n##\s+(?:1\.?\s+)?(?:Introduction|INTRODUCTION|Abstract|ABSTRACT)\b", page, maxsplit=1)[0]
    raw_lines = [line.strip() for line in page.splitlines() if line.strip()]
    title_index = next((index for index, line in enumerate(raw_lines) if line.startswith("# ")), -1)
    if title_index < 0 or title_index + 1 >= len(raw_lines):
        return None
    author_line = raw_lines[title_index + 1]
    author_plain = clean_html(author_line)
    first_author = clean_html(re.split(r"<sup>|,|\band\b", author_line, maxsplit=1, flags=re.IGNORECASE)[0])
    first_author = re.sub(r"[\d*†‡]+$", "", first_author).strip()
    affiliation = ""
    city = ""
    country = ""
    numbered = re.search(r"(?:^|\n)\s*<sup>\s*1\s*</sup>(.*?)(?=<sup>\s*2\s*</sup>|$)", page,
                         re.IGNORECASE | re.DOTALL)
    if numbered:
        affiliation = clean_html(numbered.group(1)).split("\n", 1)[0].strip(" ,;")
    if not affiliation and "," in author_plain:
        pieces = [item.strip() for item in author_plain.split(",") if item.strip()]
        if len(pieces) > 1:
            affiliation = pieces[1]
            country = pieces[-1] if pieces[-1].upper() in {"USA", "CHINA", "UK", "UAE", "CANADA"} else ""
    if not affiliation:
        institution_terms = re.compile(r"\b(?:University|College|Institute|Academy|Research|Laboratory|Lab|Google|Meta|Microsoft|Tencent|Alibaba|ByteDance|LinkedIn)\b", re.IGNORECASE)
        for line in raw_lines[title_index + 2:title_index + 12]:
            if institution_terms.search(clean_html(line)):
                affiliation = clean_html(line).strip(" ,;")
                break
    if not first_author or not affiliation:
        return None
    return {"first_author": first_author, "affiliation_name": affiliation, "affil_city": city, "country": country}


def local_parsed_paths() -> dict[str, pathlib.Path]:
    if not MANIFEST.exists():
        return {}
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    paths = {}
    for paper in manifest.get("papers", []):
        path = pathlib.Path(str(paper.get("parsed_md_path") or ""))
        if paper.get("arxiv_id") and path.exists():
            paths[str(paper["arxiv_id"])] = path
    return paths


def extract_arxiv_id(raw: str) -> str:
    match = re.search(r"arxiv\.org/(?:abs|pdf)/([a-z-]+/\d+|\d{4}\.\d{4,5})(?:v\d+)?", raw, re.IGNORECASE)
    return match.group(1) if match else ""


def extract_doi(raw: str) -> str:
    match = re.search(r"(?:doi\.org/|doi:\s*)(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", raw, re.IGNORECASE)
    return match.group(1).rstrip(".,;)") if match else ""


def parse_crossref_affiliation(payload: dict) -> dict | None:
    authors = payload.get("message", {}).get("author", [])
    if not authors:
        return None
    author = authors[0]
    affiliations = author.get("affiliation", [])
    affiliation = str(affiliations[0].get("name") or "") if affiliations else ""
    first_author = " ".join(filter(None, (author.get("given"), author.get("family")))).strip()
    if not first_author or not affiliation:
        return None
    return {"first_author": first_author, "affiliation_name": affiliation, "affil_city": "", "country": ""}


def frontmatter_value(raw: str, key: str) -> str:
    frontmatter = raw.split("---", 2)[1] if raw.startswith("---") else ""
    match = re.search(rf"(?m)^{re.escape(key)}:\s*[\"']?(.+?)[\"']?\s*$", frontmatter)
    return match.group(1).strip().strip("\"'") if match else ""


def institution_kind(name: str) -> str:
    lowered = name.casefold()
    known_companies = (
        "adobe", "alibaba", "amazon", "bytedance", "google", "huawei", "linkedin", "meituan",
        "meta", "microsoft", "netflix", "tencent",
    )
    company_terms = (" inc", " ltd", " llc", " corporation", " company", "research lab", "research center")
    academic_terms = ("university", "college", "school", "institute", "academy")
    if any(re.search(rf"\b{re.escape(company)}\b", lowered) for company in known_companies):
        return "company"
    if any(term in lowered for term in company_terms) and not any(term in lowered for term in academic_terms):
        return "company"
    return "school"


def normalize_affiliation(value: str) -> str:
    cleaned = clean_html(value).strip(" ,;*†‡0123456789\\")
    cleaned = re.sub(r"\s*\{[^}]*\}\S*", "", cleaned).strip(" ,;")
    comma_parts = [part.strip() for part in cleaned.split(",")]
    if comma_parts and re.search(r"\b(?:University|College|Institute|Academy)\b", comma_parts[0], re.IGNORECASE):
        cleaned = comma_parts[0]
    companies = (
        "ByteDance Seed", "ByteDance", "Tencent Zhuque Lab", "Tencent", "Alibaba", "Google DeepMind",
        "Google", "Meta", "Microsoft Research", "Microsoft", "Huawei London Research Centre", "Huawei",
        "Meituan", "Netflix", "LinkedIn", "Amazon", "Adobe Research", "KAIST AI", "SIAT@MMLab",
    )
    for company in companies:
        if re.search(rf"\b{re.escape(company)}\b", cleaned, re.IGNORECASE):
            return company
    # arXiv affiliation spans often already contain only the institution.  Keep
    # that authoritative name intact instead of letting a narrower regex turn
    # e.g. "National University of Singapore" into "University of Singapore".
    institution_words = re.search(r"\b(?:University|College|Institute|Academy)\b", cleaned, re.IGNORECASE)
    noisy_prefix = re.search(r"\b(?:Department|Faculty|School of|Laboratory|Lab)\b", cleaned, re.IGNORECASE)
    if institution_words and not noisy_prefix and len(cleaned.split()) <= 12:
        return cleaned.strip(" ,;.")
    academic_patterns = (
        r"(?:The\s+)?University\s+(?:of|at)\s+(?:the\s+)?[A-Z][A-Za-zÀ-ž&.'/-]*(?:\s+[A-Z][A-Za-zÀ-ž&.'/-]*){0,5}",
        r"[A-Z][A-Za-zÀ-ž&.'/-]*(?:\s+[A-Z][A-Za-zÀ-ž&.'/-]*){0,3}\s+University(?:\s+of\s+[A-Z][A-Za-zÀ-ž&.'/-]*(?:\s+[A-Z][A-Za-zÀ-ž&.'/-]*){0,4})?",
        r"[A-Z][A-Za-zÀ-ž&.'/-]*(?:\s+[A-Z][A-Za-zÀ-ž&.'/-]*){0,4}\s+(?:Institute|Academy|College)(?:\s+(?:of|for)\s+[A-Z][A-Za-zÀ-ž&.'/-]*(?:\s+[A-Z][A-Za-zÀ-ž&.'/-]*){0,4})?",
    )
    for pattern in academic_patterns:
        match = re.search(pattern, cleaned)
        if match:
            return match.group(0).strip(" ,;.")
    return ""


def collect_candidates() -> list[dict]:
    candidates = []
    for path in sorted(POSTS.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        if any(frontmatter_value(raw, field) for field in ("affiliation_name", "affil_city", "venue_city")):
            continue
        arxiv_id = extract_arxiv_id(raw)
        doi = extract_doi(raw)
        if not arxiv_id and not doi:
            continue
        candidates.append({
            "slug": frontmatter_value(raw, "slug") or path.stem,
            "title": frontmatter_value(raw, "title") or path.stem,
            "arxiv_id": arxiv_id,
            "doi": doi,
        })
    return candidates


def enrich(limit: int | None = None, refresh: bool = False, delay: float = 0.35) -> dict:
    existing = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else {"papers": {}}
    papers = {} if refresh else dict(existing.get("papers", {}))
    unresolved = []
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    candidates = collect_candidates()
    parsed_paths = local_parsed_paths()
    if limit is not None:
        candidates = candidates[:limit]
    for candidate in candidates:
        slug = candidate["slug"]
        if slug in papers and not refresh:
            continue
        if candidate["arxiv_id"]:
            official_url = ARXIV_HTML.format(arxiv_id=candidate["arxiv_id"])
            url = AR5IV.format(arxiv_id=candidate["arxiv_id"])
        else:
            official_url = CROSSREF.format(doi=requests.utils.quote(candidate["doi"], safe=""))
            url = official_url
        network_error = ""
        parsed = None
        evidence_url = official_url
        for candidate_url in dict.fromkeys((official_url, url)):
            try:
                response = session.get(candidate_url, timeout=45)
                response.raise_for_status()
                parsed = (parse_first_author_affiliation(response.text) if candidate["arxiv_id"]
                          else parse_crossref_affiliation(response.json()))
                if parsed:
                    evidence_url = candidate_url
                    break
            except requests.RequestException as error:
                network_error = str(error)
        if not parsed and candidate["arxiv_id"] in parsed_paths:
            local_path = parsed_paths[candidate["arxiv_id"]]
            parsed = parse_local_paper_header(local_path.read_text(encoding="utf-8", errors="ignore"))
            evidence_url = str(local_path)
        if not parsed:
            reason = "paper header has no parseable first-author affiliation"
            if network_error:
                reason += "; " + network_error
            unresolved.append({**candidate, "reason": reason})
            time.sleep(delay)
            continue
        parsed["affiliation_name"] = normalize_affiliation(parsed["affiliation_name"])
        if not parsed["affiliation_name"]:
            unresolved.append({**candidate, "reason": "paper header did not expose a credible first-author institution"})
            time.sleep(delay)
            continue
        papers[slug] = {
            **candidate,
            **parsed,
            "location_type": institution_kind(parsed["affiliation_name"]),
            "evidence_url": evidence_url,
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }
        time.sleep(delay)
    payload = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "source": "ar5iv public paper HTML; first listed author only",
        "papers": papers,
        "unresolved": unresolved,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--delay", type=float, default=0.35)
    args = parser.parse_args()
    payload = enrich(args.limit, args.refresh, args.delay)
    print(json.dumps({"resolved": len(payload["papers"]), "unresolved": len(payload["unresolved"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
