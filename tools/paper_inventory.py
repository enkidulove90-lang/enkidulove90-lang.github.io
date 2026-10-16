#!/usr/bin/env python3
"""Build a deterministic publication manifest keyed by arXiv ID."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path


ARXIV_ID = re.compile(r"(?<!\d)(\d{4}\.\d{4,5})(?!\d)")
ENGLISH_TITLE = re.compile(r"(?im)^\*\*英文标题\*\*\s*[:：]\s*(.+?)\s*$")
HEADING = re.compile(r"(?m)^#\s+(.+?)\s*$")


@dataclass(frozen=True)
class PaperRecord:
    arxiv_id: str
    pdf_path: str
    summary_path: str | None
    parsed_md_path: str | None
    on_site: bool
    quality_state: str
    parsed_title: str | None = None
    summary_title: str | None = None
    title_fingerprint: str | None = None
    reasons: list[str] = field(default_factory=list)


def _id_from_name(path: Path) -> str | None:
    match = ARXIV_ID.search(path.name)
    return match.group(1) if match else None


def _first(mapping: dict[str, list[Path]], paper_id: str) -> Path | None:
    values = mapping.get(paper_id, [])
    if not values:
        return None
    return sorted(values, key=lambda path: (-path.stat().st_size, str(path).lower()))[0]


def _index_files(root: Path, pattern: str, recursive: bool = False) -> dict[str, list[Path]]:
    result: dict[str, list[Path]] = {}
    iterator = root.rglob(pattern) if recursive and root.exists() else root.glob(pattern) if root.exists() else []
    for path in iterator:
        paper_id = _id_from_name(path)
        if paper_id:
            result.setdefault(paper_id, []).append(path.resolve())
    return result


def _read_text(path: Path | None) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path else ""


def _parsed_title(path: Path | None) -> str | None:
    match = HEADING.search(_read_text(path))
    if not match:
        return None
    title = match.group(1).strip()
    return None if ARXIV_ID.fullmatch(title) else title


def _summary_title(path: Path | None) -> str | None:
    text = _read_text(path)
    match = ENGLISH_TITLE.search(text) or HEADING.search(text)
    return match.group(1).strip() if match else None


def _title_tokens(title: str | None) -> set[str]:
    if not title:
        return set()
    normalized = unicodedata.normalize("NFKC", title).casefold()
    normalized = re.sub(r"</?[^>]+>", "", normalized)
    return {token for token in re.findall(r"[a-z0-9]+", normalized) if len(token) > 1}


def _title_mismatch(parsed_title: str | None, summary_title: str | None) -> bool:
    parsed = _title_tokens(parsed_title)
    summary = _title_tokens(summary_title)
    if len(parsed) < 2 or len(summary) < 2:
        return False
    overlap = len(parsed & summary) / min(len(parsed), len(summary))
    return overlap < 0.5


def _site_ids(posts_dir: Path) -> set[str]:
    ids: set[str] = set()
    if not posts_dir.exists():
        return ids
    for post in posts_dir.glob("*.md"):
        match = ARXIV_ID.search(post.read_text(encoding="utf-8", errors="replace"))
        if match:
            ids.add(match.group(1))
    return ids


def _excluded_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(item) for item in data.get("excluded_ids", [])}


def build_manifest(
    papers_dir: Path,
    summaries_dir: Path,
    parsed_dir: Path,
    posts_dir: Path,
    exclusions_path: Path,
) -> list[PaperRecord]:
    pdfs = _index_files(Path(papers_dir), "*.pdf")
    summaries = _index_files(Path(summaries_dir), "*.md")
    parsed = _index_files(Path(parsed_dir), "*.md", recursive=True)
    published = _site_ids(Path(posts_dir))
    excluded = _excluded_ids(Path(exclusions_path))

    duplicates = sorted(paper_id for paper_id, paths in pdfs.items() if len(paths) > 1)
    if duplicates:
        raise ValueError(f"duplicate PDF arXiv ID {duplicates[0]}")

    records: list[PaperRecord] = []
    for paper_id in sorted(pdfs):
        if paper_id in excluded:
            continue
        pdf = pdfs[paper_id][0]
        summary = _first(summaries, paper_id)
        parsed_md = _first(parsed, paper_id)
        parsed_title = _parsed_title(parsed_md)
        summary_title = _summary_title(summary)
        reasons: list[str] = []

        if paper_id in published:
            state = "published"
        elif not parsed_md:
            state = "needs_parse"
        elif not summary:
            state = "needs_summary"
        elif _title_mismatch(parsed_title, summary_title):
            state = "needs_summary"
            reasons.append("title mismatch")
        else:
            state = "ready"

        tokens = sorted(_title_tokens(parsed_title))
        records.append(
            PaperRecord(
                arxiv_id=paper_id,
                pdf_path=str(pdf),
                summary_path=str(summary) if summary else None,
                parsed_md_path=str(parsed_md) if parsed_md else None,
                on_site=paper_id in published,
                quality_state=state,
                parsed_title=parsed_title,
                summary_title=summary_title,
                title_fingerprint=" ".join(tokens) or None,
                reasons=reasons,
            )
        )
    return records


def write_manifest(records: list[PaperRecord], output: Path) -> None:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": 1, "papers": [asdict(record) for record in sorted(records, key=lambda r: r.arxiv_id)]}
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library-root", type=Path, default=Path("D:/recommendation-system-learning"))
    parser.add_argument("--posts-dir", type=Path, default=Path(__file__).resolve().parents[1] / "source" / "_posts")
    parser.add_argument("--exclusions", type=Path, default=Path(__file__).with_name("paper_exclusions.json"))
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("paper_publication_manifest.json"))
    args = parser.parse_args()
    data = args.library_root / "data"
    records = build_manifest(data / "papers", data / "summaries", data / "parsed", args.posts_dir, args.exclusions)
    write_manifest(records, args.output)
    counts: dict[str, int] = {}
    for record in records:
        counts[record.quality_state] = counts.get(record.quality_state, 0) + 1
    print(json.dumps({"total": len(records), "states": counts, "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
