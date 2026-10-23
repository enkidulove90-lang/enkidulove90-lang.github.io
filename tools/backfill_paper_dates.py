#!/usr/bin/env python3
"""Backfill Hexo paper dates from arXiv or Crossref authoritative metadata."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode
import xml.etree.ElementTree as ET

import requests


ARXIV_ID = re.compile(
    r"(?im)^(?:arxiv_id:\s*[\"']?|.*?arxiv\.org/(?:abs|pdf)/)"
    r"(\d{4}\.\d{4,5})(?:v\d+)?"
)
DOI = re.compile(r"(?i)(?:doi\s*:\s*|https?://doi\.org/)(10\.\d{4,9}/[^\s<>\])]+)")
DATE_LINE = re.compile(r"(?m)^date:\s*[^\r\n]+$")
ATOM = {"atom": "http://www.w3.org/2005/Atom"}


def extract_identity(markdown: str) -> tuple[str, str]:
    arxiv = ARXIV_ID.search(markdown)
    if arxiv:
        return "arxiv", arxiv.group(1)
    doi = DOI.search(markdown)
    if doi:
        return "doi", doi.group(1).rstrip(".,;)")
    return "", ""


def parse_arxiv_dates(xml_text: str) -> dict[str, str]:
    root = ET.fromstring(xml_text)
    dates: dict[str, str] = {}
    for entry in root.findall("atom:entry", ATOM):
        identity = entry.findtext("atom:id", default="", namespaces=ATOM)
        published = entry.findtext("atom:published", default="", namespaces=ATOM)
        match = re.search(r"/(\d{4}\.\d{4,5})(?:v\d+)?$", identity)
        if match and re.fullmatch(r"\d{4}-\d{2}-\d{2}T.*", published):
            dates[match.group(1)] = published[:10]
    return dates


def crossref_publication_date(message: dict[str, Any]) -> str:
    for key in ("published-online", "published-print", "published", "issued", "created"):
        parts = ((message.get(key) or {}).get("date-parts") or [])
        if not parts:
            continue
        values = list(parts[0])
        if len(values) >= 2:
            year, month = int(values[0]), int(values[1])
            day = int(values[2]) if len(values) >= 3 else 1
            return f"{year:04d}-{month:02d}-{day:02d}"
    return ""


def datacite_publication_date(attributes: dict[str, Any]) -> str:
    for key in ("published", "publicationYear", "created", "registered"):
        value = str(attributes.get(key) or "")
        match = re.match(r"^(\d{4})-(\d{2})-(\d{2})", value)
        if match:
            return match.group(0)
    return ""


def override_publication_date(overrides: dict[str, Any], identity: str) -> str:
    record = overrides.get(identity) or {}
    date = str(record.get("date") or "")
    source = str(record.get("source") or "")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", date) and source.startswith("https://"):
        return date
    return ""


def apply_publication_date(markdown: str, published_date: str) -> str:
    frontmatter_end = markdown.find("---", 3)
    if frontmatter_end < 0:
        raise ValueError("post has no complete frontmatter")
    frontmatter = markdown[:frontmatter_end]
    if not DATE_LINE.search(frontmatter):
        raise ValueError("post frontmatter has no date")
    return DATE_LINE.sub(f"date: {published_date}", markdown, count=1)


def _session() -> requests.Session:
    session = requests.Session()
    session.trust_env = False
    session.headers.update({"User-Agent": "enkidu-paper-date-backfill/1.0"})
    return session


def fetch_arxiv_dates(session: requests.Session, identities: list[str]) -> dict[str, str]:
    dates: dict[str, str] = {}
    for offset in range(0, len(identities), 50):
        batch = identities[offset : offset + 50]
        url = "https://export.arxiv.org/api/query?" + urlencode(
            {"id_list": ",".join(batch), "max_results": len(batch)}
        )
        response = session.get(url, timeout=30)
        response.raise_for_status()
        dates.update(parse_arxiv_dates(response.text))
    return dates


def fetch_crossref_date(session: requests.Session, doi: str) -> str:
    response = session.get(
        "https://api.crossref.org/works/" + quote(doi, safe=""),
        timeout=20,
    )
    response.raise_for_status()
    return crossref_publication_date(response.json().get("message") or {})


def fetch_datacite_date(session: requests.Session, doi: str) -> str:
    response = session.get(
        "https://api.datacite.org/dois/" + quote(doi, safe=""),
        timeout=20,
    )
    response.raise_for_status()
    attributes = ((response.json().get("data") or {}).get("attributes") or {})
    return datacite_publication_date(attributes)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--posts", type=Path, default=Path(__file__).resolve().parents[1] / "source" / "_posts")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument(
        "--overrides",
        type=Path,
        default=Path(__file__).with_name("paper_date_overrides.json"),
    )
    args = parser.parse_args()

    records: list[tuple[Path, str, str, str]] = []
    for path in sorted(args.posts.glob("*.md")):
        markdown = path.read_text(encoding="utf-8")
        kind, identity = extract_identity(markdown)
        current = (DATE_LINE.search(markdown) or [""])[0].partition(":")[2].strip()
        if kind and identity:
            records.append((path, kind, identity, current))

    session = _session()
    overrides = json.loads(args.overrides.read_text(encoding="utf-8")) if args.overrides.is_file() else {}
    arxiv_dates = fetch_arxiv_dates(
        session,
        sorted({identity for _, kind, identity, _ in records if kind == "arxiv"}),
    )
    doi_dates: dict[str, str] = {}
    for identity in sorted({identity for _, kind, identity, _ in records if kind == "doi"}):
        try:
            doi_dates[identity] = fetch_crossref_date(session, identity)
        except requests.RequestException:
            doi_dates[identity] = ""
        if not doi_dates[identity]:
            try:
                doi_dates[identity] = fetch_datacite_date(session, identity)
            except requests.RequestException:
                doi_dates[identity] = ""
        if not doi_dates[identity]:
            doi_dates[identity] = override_publication_date(overrides, identity)

    report = {"updated": [], "unchanged": [], "unresolved": []}
    for path, kind, identity, current in records:
        resolved = arxiv_dates.get(identity, "") if kind == "arxiv" else doi_dates.get(identity, "")
        item = {"file": path.name, "identity": identity, "date": resolved or None}
        if not resolved:
            report["unresolved"].append(item)
        elif resolved == current:
            report["unchanged"].append(item)
        else:
            report["updated"].append({**item, "previous_date": current})
            if args.apply:
                markdown = path.read_text(encoding="utf-8")
                path.write_text(apply_publication_date(markdown, resolved), encoding="utf-8")

    output = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report:
        args.report.write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if not report["unresolved"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
