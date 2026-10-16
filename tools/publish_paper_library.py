#!/usr/bin/env python3
"""Orchestrate audited paper preparation; defaults to a no-write dry run."""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path

from mineru_adapter import MinerUUnavailable, ParseRequired, prepare_assets
from notion_publish import NotionClient, publish_article
from paper_article import build_article, materialize_article, validate_article
from paper_inventory import build_manifest


@dataclass(frozen=True)
class PipelineConfig:
    library_root: Path
    site_root: Path
    exclusions: Path
    batch: str = "ready"
    ids: tuple[str, ...] = ()
    run_mineru: bool = False
    write_notion: bool = False
    promote: bool = False
    materialize: bool = False
    database_id: str = ""
    token: str = ""
    state_path: Path | None = None
    refresh_existing: bool = False


def _load_completed(path: Path | None) -> set[str]:
    if not path or not path.exists():
        return set()
    return set(json.loads(path.read_text(encoding="utf-8")).get("completed", []))


def _save_completed(path: Path, completed: set[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"completed": sorted(completed)}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def run_pipeline(config: PipelineConfig) -> dict:
    data = Path(config.library_root) / "data"
    records = build_manifest(
        data / "papers",
        data / "summaries",
        data / "parsed",
        Path(config.site_root) / "source" / "_posts",
        Path(config.exclusions),
    )
    if config.refresh_existing:
        if not config.ids:
            raise ValueError("refresh_existing requires explicit paper IDs")
        selected = [record for record in records if record.on_site]
    else:
        selected = [record for record in records if not record.on_site]
    if config.batch != "all" and not config.refresh_existing:
        selected = [record for record in selected if record.quality_state == config.batch]
    if config.ids:
        wanted = set(config.ids)
        selected = [record for record in selected if record.arxiv_id in wanted]
    selected.sort(key=lambda record: record.arxiv_id)

    completed = _load_completed(config.state_path)
    client = None
    if config.write_notion:
        if not config.database_id:
            raise ValueError("NOTION_DATABASE_ID is required for write mode")
        client = NotionClient(config.token)

    items: list[dict] = []
    for record in selected:
        if record.arxiv_id in completed and not config.refresh_existing:
            items.append({"arxiv_id": record.arxiv_id, "state": record.quality_state, "action": "skipped_completed", "errors": []})
            continue
        if record.quality_state == "needs_summary":
            items.append({"arxiv_id": record.arxiv_id, "state": record.quality_state, "action": "blocked", "errors": ["reliable summary required"]})
            continue
        if record.quality_state == "needs_parse" and not config.run_mineru:
            items.append({"arxiv_id": record.arxiv_id, "state": record.quality_state, "action": "blocked", "errors": ["MinerU parse required"]})
            continue
        try:
            parsed = prepare_assets(
                record,
                Path(config.site_root) / ".paper-work",
                run_mineru=config.run_mineru,
            )
            summary = Path(record.summary_path) if record.summary_path else None
            draft = build_article(record, parsed, summary, include_source_pdf=True)
            errors = validate_article(draft)
            if errors:
                items.append({"arxiv_id": record.arxiv_id, "state": record.quality_state, "action": "blocked", "errors": errors})
                continue
            if config.materialize:
                materialize_article(draft, config.site_root)
            result = publish_article(
                client,
                draft,
                config.database_id,
                write=config.write_notion,
                promote=config.promote,
            )
            action = result.action
            if config.materialize and not config.write_notion:
                action = "materialized"
            items.append(
                {
                    "arxiv_id": record.arxiv_id,
                    "title": draft.title,
                    "state": record.quality_state,
                    "action": action,
                    "figure_count": len(draft.figures),
                    "figure_provenance": sorted(
                        {figure.provenance for figure in draft.figures}
                    ),
                    "source_pdf": draft.source_pdf is not None,
                    "errors": [],
                }
            )
            if config.materialize or config.write_notion:
                completed.add(record.arxiv_id)
        except (ParseRequired, MinerUUnavailable, ValueError) as error:
            items.append({"arxiv_id": record.arxiv_id, "state": record.quality_state, "action": "blocked", "errors": [str(error)]})

    if (config.materialize or config.write_notion) and config.state_path:
        _save_completed(Path(config.state_path), completed)
    blocked_count = sum(item["action"] == "blocked" for item in items)
    return {
        "schema_version": 1,
        "mode": "write" if config.write_notion else "dry_run",
        "batch": config.batch,
        "selected_count": len(items),
        "publishable_count": len(items) - blocked_count,
        "blocked_count": blocked_count,
        "items": items,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--library-root", type=Path, default=Path("D:/recommendation-system-learning"))
    parser.add_argument("--site-root", type=Path, default=root)
    parser.add_argument("--exclusions", type=Path, default=root / "tools" / "paper_exclusions.json")
    parser.add_argument("--batch", choices=("ready", "needs_summary", "needs_parse", "all"), default="ready")
    parser.add_argument("--ids", default="")
    parser.add_argument("--run-mineru", action="store_true")
    parser.add_argument("--write-notion", action="store_true")
    parser.add_argument("--promote", action="store_true")
    parser.add_argument("--materialize", action="store_true")
    parser.add_argument("--refresh-existing", action="store_true")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--state", type=Path, default=root / "tools" / ".paper_publication_state.json")
    args = parser.parse_args()
    report = run_pipeline(
        PipelineConfig(
            library_root=args.library_root,
            site_root=args.site_root,
            exclusions=args.exclusions,
            batch=args.batch,
            ids=tuple(item.strip() for item in args.ids.split(",") if item.strip()),
            run_mineru=args.run_mineru,
            write_notion=args.write_notion,
            promote=args.promote,
            materialize=args.materialize,
            database_id=os.environ.get("NOTION_DATABASE_ID", ""),
            token=os.environ.get("NOTION_TOKEN", ""),
            state_path=args.state,
            refresh_existing=args.refresh_existing,
        )
    )
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 1 if any(item["action"] == "blocked" for item in report["items"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
