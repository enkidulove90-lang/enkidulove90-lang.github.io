#!/usr/bin/env python3
"""Verify migrated Notion article content against the local Hexo source.

This module is intentionally read-only.  It retrieves Notion's enhanced
Markdown representation, downloads the attached images, and compares both
the normalized prose and SHA-256 image hashes with the local migration plan.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable
from urllib.parse import urlsplit

import requests

from notion_content_migration import (
    ImagePart,
    MigrationPost,
    _load_env_file,
    build_migration_plan,
    build_orphan_asset_posts,
)
from notion_publish import NotionClient


REMOTE_IMAGE_RE = re.compile(r"!\[[^\]]*\]\((https?://[^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")


@dataclass
class AuditResult:
    slug: str
    verified: bool
    errors: list[str]
    local_image_hashes: list[str]
    remote_image_hashes: list[str]
    page_id: str | None = None


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _normalize_text(markdown: str) -> str:
    """Normalize prose while ignoring image URLs that Notion rewrites."""
    text = REMOTE_IMAGE_RE.sub("", markdown)
    def normalize_link(match: re.Match) -> str:
        label, target = match.group(1), match.group(2)
        parsed = urlsplit(target)
        if parsed.netloc.lower() == "app.notion.com":
            target = parsed.path or "/"
        if label == target:
            return target
        bare_target = re.sub(r"^https?://", "", target, flags=re.I).rstrip("/")
        if label.rstrip("/").lower() == bare_target.lower():
            return label
        return f"[{label}]({target})"

    text = MARKDOWN_LINK_RE.sub(normalize_link, text)
    for _ in range(3):
        decoded = html.unescape(text)
        if decoded == text:
            break
        text = decoded
    text = re.sub(r"(?m)^\s*```[^\n]*$", "", text)
    text = text.replace("`", "")
    text = text.replace("\\", "")
    text = re.sub(r"</?(?:sub|sup)\s*>", "", text, flags=re.I)
    text = re.sub(r"</?(?:table|tr|td|thead|tbody|br)(?:\s+[^>]*)?>", " ", text, flags=re.I)
    lines: list[str] = []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines():
        stripped = line.strip()
        if stripped == "\\":
            continue
        if stripped.startswith("```"):
            continue
        if "-" in stripped and re.fullmatch(r"[\s|:-]+", stripped):
            continue
        lines.append(line.replace("\\|", "|").replace("|", " "))
    text = "\n".join(lines).replace("**", "").replace("_", "")
    text = re.sub(r"\\([{}\[\]_*#>])", r"\1", text)
    text = text.replace("$", "")
    text = text.replace("—", "-")
    text = re.sub(r"(?<!\S)--(?!\S)", "-", text)
    return " ".join(text.split())


def _local_markdown(post: MigrationPost) -> str:
    return "\n".join(part.markdown for part in post.parts if hasattr(part, "markdown"))


def _download_with_retry(
    url: str,
    *,
    request_get=requests.get,
    max_retries: int = 5,
    backoff: float = 1.0,
) -> bytes:
    for attempt in range(max_retries + 1):
        try:
            response = request_get(url, timeout=120)
            response.raise_for_status()
            return response.content
        except requests.RequestException:
            if attempt >= max_retries:
                raise
            time.sleep(backoff * (2**attempt))
    raise RuntimeError("unreachable")


def _default_download(url: str) -> bytes:
    return _download_with_retry(url)


def audit_post(
    client,
    database_id: str,
    post: MigrationPost,
    download: Callable[[str], bytes] = _default_download,
    page: dict | None = None,
    verify_images: bool = True,
) -> AuditResult:
    errors: list[str] = []
    local_hashes = [part.sha256 for part in post.parts if isinstance(part, ImagePart)]
    remote_hashes: list[str] = []

    try:
        page = page or client.find_page_by_slug(database_id, post.slug)
    except requests.RequestException:
        return AuditResult(post.slug, False, ["remote_request_failed"], local_hashes, [])
    if not page:
        return AuditResult(post.slug, False, ["missing_remote_page"], local_hashes, [])

    page_id = page["id"]
    try:
        remote = client.retrieve_markdown(page_id)
    except requests.RequestException:
        return AuditResult(post.slug, False, ["remote_request_failed"], local_hashes, [], page_id)
    if remote.get("truncated") or remote.get("unknown_block_ids"):
        errors.append("remote_content_truncated")

    remote_markdown = remote.get("markdown", "")
    if _normalize_text(_local_markdown(post)) != _normalize_text(remote_markdown):
        errors.append("text_mismatch")

    if verify_images:
        for url in REMOTE_IMAGE_RE.findall(remote_markdown):
            try:
                remote_hashes.append(_sha256(download(url)))
            except Exception:
                errors.append("image_download_failed")

        if Counter(local_hashes) != Counter(remote_hashes):
            errors.append("image_hash_mismatch")

    errors = list(dict.fromkeys(errors))
    return AuditResult(post.slug, not errors, errors, local_hashes, remote_hashes, page_id)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit local article text/images against Notion")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--report", type=Path)
    parser.add_argument("--text-only", action="store_true", help="skip image downloads while tuning text audit")
    args = parser.parse_args()

    root = args.root.resolve()
    _load_env_file(root / ".env")
    _load_env_file(root / ".env.local")
    token = os.environ.get("NOTION_TOKEN")
    database_id = os.environ.get("NOTION_DATABASE_ID")
    if not token or not database_id:
        print("NOTION_TOKEN and NOTION_DATABASE_ID are required for cloud audit.", file=sys.stderr)
        return 2

    plan = build_migration_plan(root)
    client = NotionClient(token)
    posts = [*plan.posts, *build_orphan_asset_posts(plan)]
    pages_by_slug = client.list_pages_by_slug(database_id)
    results = []
    for post in posts:
        if post.slug not in pages_by_slug:
            local_hashes = [part.sha256 for part in post.parts if isinstance(part, ImagePart)]
            results.append(AuditResult(post.slug, False, ["missing_remote_page"], local_hashes, []))
        else:
            results.append(
                audit_post(
                    client,
                    database_id,
                    post,
                    page=pages_by_slug[post.slug],
                    verify_images=not args.text_only,
                )
            )
    payload = {
        "summary": {
            "total": len(results),
            "verified": sum(result.verified for result in results),
            "failed": sum(not result.verified for result in results),
        },
        "results": [asdict(result) for result in results],
    }
    report = (args.report or root / "reports" / "notion-content-audit.json").resolve()
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    print(f"Report: {report}")
    return 0 if payload["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
