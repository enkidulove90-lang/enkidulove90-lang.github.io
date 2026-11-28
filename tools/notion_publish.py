#!/usr/bin/env python3
"""Idempotently publish validated paper drafts to Notion."""

from __future__ import annotations

import hashlib
import logging
import math
import mimetypes
import re
import time
from dataclasses import dataclass
from pathlib import Path

import requests

from paper_article import ArticleDraft, check_article, validate_article
from paper_identity import canWriteSafely, identityKey


API = "https://api.notion.com/v1"
API_VERSION = "2026-03-11"
IMAGE_LINE = re.compile(r"^!\[[^]]*\]\(/images/papers/[^/]+/([^)]+)\)$")
logger = logging.getLogger(__name__)
_METADATA_TYPES = {"venue_name": "rich_text", "venue_type": "select", "year": "select",
                   "category": "select", "tags": "multi_select", "authors": "rich_text",
                   "summary": "rich_text", "arxiv_id": "rich_text",
                   "location_type": "rich_text", "venue_city": "rich_text", "affil_city": "multi_select",
                   "corresponding_city": "rich_text", "affiliation_name": "rich_text"}
# The five geography fields shared by the review package and the site map pipeline.
LOCATION_FIELDS = ("location_type", "venue_city", "affil_city", "corresponding_city", "affiliation_name")
#: Publication date, never the Notion page creation time. Kept apart from
#: _METADATA_TYPES because Notion encodes dates as ``{"date": {"start": ...}}``.
DATE_FIELD = "date"


@dataclass(frozen=True)
class PublishResult:
    arxiv_id: str
    action: str
    page_id: str | None = None
    status: str = "Invisible"
    identity_key: str = ""
    overwrite_snapshot: str = ""


class RequestsTransport:
    def __init__(self, token: str, api_version: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": api_version,
        }
        self.session = requests.Session()

    def request(self, method: str, path: str, **kwargs):
        headers = dict(self.headers)
        if "files" not in kwargs:
            headers["Content-Type"] = "application/json"
        try:
            response = self.session.request(method, API + path, headers=headers, timeout=120, **kwargs)
        except requests.exceptions.SSLError:
            self.session.close()
            self.session = requests.Session()
            raise
        response.raise_for_status()
        return response.json() if response.content else {}


class NotionClient:
    def __init__(
        self,
        token: str,
        *,
        transport=None,
        api_version: str = API_VERSION,
        multipart_threshold: int = 20 * 1024 * 1024,
        part_size: int = 10 * 1024 * 1024,
        max_retries: int = 5,
        retry_backoff: float = 1.0,
    ):
        if not token:
            raise ValueError("Notion token is required for write mode")
        self.transport = transport or RequestsTransport(token, api_version)
        self.multipart_threshold = multipart_threshold
        self.part_size = part_size
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self._upload_cache: dict[str, str] = {}
        self._data_sources: dict[str, str] = {}
        self._property_names: set[str] | None = None
        self._property_types: dict[str, str] = {}

    def _request(self, method: str, path: str, **kwargs):
        file_positions: list[tuple[object, int]] = []
        for value in (kwargs.get("files") or {}).values():
            payload = value[1] if isinstance(value, tuple) and len(value) > 1 else value
            if hasattr(payload, "tell") and hasattr(payload, "seek"):
                file_positions.append((payload, payload.tell()))
        for attempt in range(self.max_retries + 1):
            for handle, position in file_positions:
                handle.seek(position)
            try:
                return self.transport.request(method, path, **kwargs)
            except requests.RequestException as exc:
                status = getattr(getattr(exc, "response", None), "status_code", None)
                transient = status is None or status == 429 or status >= 500
                if not transient or attempt >= self.max_retries:
                    raise
                retry_after = getattr(getattr(exc, "response", None), "headers", {}).get("Retry-After")
                delay = float(retry_after) if retry_after else self.retry_backoff * (2**attempt)
                time.sleep(delay)

    def _data_source_id(self, database_id: str) -> str:
        if database_id not in self._data_sources:
            database = self._request("GET", f"/databases/{database_id}")
            sources = database.get("data_sources") or []
            self._data_sources[database_id] = sources[0]["id"] if sources else database_id
            if sources:
                source = self._request("GET", f"/data_sources/{self._data_sources[database_id]}")
                schema = source.get("properties") or {}
                self._property_names = set(schema.keys())
                self._property_types = {name: prop.get("type", "") for name, prop in schema.items()}
        return self._data_sources[database_id]

    @staticmethod
    def _rich_text(value: str) -> list[dict]:
        return [{"type": "text", "text": {"content": value[:2000]}}] if value else []

    def _properties(self, values: dict) -> dict:
        properties = {
            "title": {"title": self._rich_text(values.get("title", ""))},
            "status": {"select": {"name": values.get("status", "Invisible")}},
            "type": {"select": {"name": "Post"}},
            "slug": {"rich_text": self._rich_text(values.get("slug", ""))},
            "summary": {"rich_text": self._rich_text(values.get("summary", ""))},
            "arxiv_id": {"rich_text": self._rich_text(values.get("arxiv_id", ""))},
        }
        # paper_key is the dedup identity: never silently drop it. If the
        # caller supplied one but the live schema lacks the column, fail loud.
        requested_key = values.get("paper_key", "")
        if requested_key and self._property_names is not None and "paper_key" not in self._property_names:
            raise ValueError("Notion schema is missing required property: paper_key")
        if requested_key or self._property_names is None:
            properties["paper_key"] = {"rich_text": self._rich_text(requested_key)}
        for name, default_type in _METADATA_TYPES.items():
            if name not in values or values[name] is None:
                continue
            if self._property_names is not None and name not in self._property_names:
                logger.warning("Notion schema does not contain property: %s", name)
                continue
            value = values[name]
            property_type = self._property_types.get(name) or default_type
            if not self._property_types.get(name):
                logger.warning("Notion property type unavailable for %s; using %s", name, default_type)
            sync_types = {"venue_name": "rich_text", "venue_type": "select", "year": "select"}
            if name in sync_types and property_type != sync_types[name]:
                logger.warning("Notion property %s uses %s but current sync reads %s", name, property_type, sync_types[name])
            if name == DATE_FIELD:
                # Handled after the loop: dates are not rich_text/select.
                continue
            if property_type == "multi_select" and name != "affil_city":
                # tags is the only free-form multi-select; keep the order the
                # editorial layer chose so the site's tag cloud stays stable.
                items = value if isinstance(value, list) else [value]
                names = [str(item).strip() for item in items if str(item).strip()]
                if names:
                    properties[name] = {"multi_select": [{"name": item} for item in names]}
                continue
            if name == "affil_city":
                # The live schema decides the shape. The historical database uses
                # Select (one city); other databases may use Multi-select. Never
                # collapse multiple cities into one Select silently.
                if property_type == "multi_select":
                    if not isinstance(value, list) or not all(isinstance(city, str) and city for city in value):
                        raise ValueError("affil_city requires a list of nonempty strings for multi_select schema")
                    properties[name] = {"multi_select": [{"name": city} for city in value]}
                elif property_type == "select":
                    if isinstance(value, list):
                        if len(value) != 1 or not isinstance(value[0], str) or not value[0]:
                            raise ValueError("affil_city needs exactly one city for a select schema")
                        value = value[0]
                    if not isinstance(value, str) or not value:
                        raise ValueError("affil_city needs a nonempty city string for a select schema")
                    properties[name] = {"select": {"name": value}}
                else:
                    raise ValueError(f"affil_city unsupported Notion schema type: {property_type}")
            elif property_type == "rich_text" and isinstance(value, str):
                properties[name] = {"rich_text": self._rich_text(value)}
            elif property_type == "select" and isinstance(value, str) and value:
                properties[name] = {"select": {"name": value}}
            else:
                raise ValueError(f"unsupported Notion schema type or value for {name}: {property_type}")
        # Publication date lives in its own Notion type; writing it here is what
        # stops notion_sync from falling back to the page creation time.
        date_value = str(values.get(DATE_FIELD) or "").strip()
        if date_value:
            properties[DATE_FIELD] = {"date": {"start": date_value[:10]}}
        if self._property_names is not None:
            for name in properties.keys() - self._property_names:
                logger.warning("Notion schema does not contain property: %s", name)
            properties = {key: value for key, value in properties.items() if key in self._property_names}
        return properties

    def find_page_by_arxiv(self, database_id: str, arxiv_id: str):
        source_id = self._data_source_id(database_id)
        payload = {
            "filter": {"property": "arxiv_id", "rich_text": {"equals": arxiv_id}},
            "page_size": 2,
        }
        result = self._request("POST", f"/data_sources/{source_id}/query", json=payload)
        pages = result.get("results") or []
        if not pages:
            return None
        page_id = pages[0]["id"]
        return {"id": page_id, "has_source_pdf": self._page_has_source_pdf(page_id)}

    def find_page_by_identity(self, database_id: str, identity_key: str):
        """Dedup on the paper_key property (works for arXiv and ACL papers)."""
        source_id = self._data_source_id(database_id)
        payload = {
            "filter": {"property": "paper_key", "rich_text": {"equals": identity_key}},
            "page_size": 2,
        }
        result = self._request("POST", f"/data_sources/{source_id}/query", json=payload)
        pages = result.get("results") or []
        if not pages:
            return None
        page_id = pages[0]["id"]
        return {"id": page_id, "has_source_pdf": self._page_has_source_pdf(page_id)}

    def find_page_by_slug(self, database_id: str, slug: str):
        source_id = self._data_source_id(database_id)
        payload = {
            "filter": {"property": "slug", "rich_text": {"equals": slug}},
            "page_size": 2,
        }
        result = self._request("POST", f"/data_sources/{source_id}/query", json=payload)
        pages = result.get("results") or []
        return {"id": pages[0]["id"]} if pages else None

    def list_pages_by_slug(self, database_id: str) -> dict[str, dict]:
        source_id = self._data_source_id(database_id)
        pages_by_slug: dict[str, dict] = {}
        cursor = None
        while True:
            payload: dict = {"page_size": 100}
            if cursor:
                payload["start_cursor"] = cursor
            result = self._request("POST", f"/data_sources/{source_id}/query", json=payload)
            for page in result.get("results") or []:
                rich_text = (page.get("properties") or {}).get("slug", {}).get("rich_text") or []
                slug = "".join(item.get("plain_text", "") for item in rich_text).strip()
                if slug:
                    pages_by_slug[slug] = {"id": page["id"]}
            if not result.get("has_more"):
                return pages_by_slug
            cursor = result.get("next_cursor")

    def _page_has_source_pdf(self, page_id: str) -> bool:
        cursor = None
        while True:
            params = {"page_size": 100}
            if cursor:
                params["start_cursor"] = cursor
            result = self._request("GET", f"/blocks/{page_id}/children", params=params)
            if any(block.get("type") == "file" for block in result.get("results", [])):
                return True
            if not result.get("has_more"):
                return False
            cursor = result.get("next_cursor")

    def create_page(self, database_id: str, properties: dict) -> str:
        source_id = self._data_source_id(database_id)
        result = self._request(
            "POST",
            "/pages",
            json={
                "parent": {"type": "data_source_id", "data_source_id": source_id},
                "properties": self._properties(properties),
            },
        )
        return result["id"]

    def update_page(self, page_id: str, properties: dict) -> None:
        self._request("PATCH", f"/pages/{page_id}", json={"properties": self._properties(properties)})

    def clear_children(self, page_id: str) -> None:
        cursor = None
        while True:
            params = {"page_size": 100}
            if cursor:
                params["start_cursor"] = cursor
            result = self._request("GET", f"/blocks/{page_id}/children", params=params)
            for block in result.get("results", []):
                self._request("DELETE", f"/blocks/{block['id']}")
            if not result.get("has_more"):
                return
            cursor = result.get("next_cursor")

    def append_children(self, page_id: str, blocks: list[dict]) -> None:
        self._request("PATCH", f"/blocks/{page_id}/children", json={"children": blocks})

    def replace_markdown(self, page_id: str, markdown: str) -> None:
        self._request(
            "PATCH",
            f"/pages/{page_id}/markdown",
            json={"type": "replace_content", "replace_content": {"new_str": markdown}},
        )

    def retrieve_markdown(self, page_id: str) -> dict:
        return self._request("GET", f"/pages/{page_id}/markdown")

    def append_markdown(self, page_id: str, markdown: str) -> None:
        self._request(
            "PATCH",
            f"/pages/{page_id}/markdown",
            json={
                "type": "insert_content",
                "insert_content": {"content": markdown, "position": {"type": "end"}},
            },
        )

    def append_uploaded_image(self, page_id: str, upload_id: str, caption: str) -> None:
        self.append_children(
            page_id,
            [
                {
                    "object": "block",
                    "type": "image",
                    "image": {
                        "type": "file_upload",
                        "file_upload": {"id": upload_id},
                        "caption": self._rich_text(caption),
                    },
                }
            ],
        )

    def upload_file(self, path: Path) -> str:
        path = Path(path)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in self._upload_cache:
            return self._upload_cache[digest]
        size = path.stat().st_size
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if size <= self.multipart_threshold:
            created = self._request(
                "POST",
                "/file_uploads",
                json={"mode": "single_part", "filename": path.name, "content_type": content_type},
            )
            upload_id = created["id"]
            with path.open("rb") as handle:
                self._request(
                    "POST",
                    f"/file_uploads/{upload_id}/send",
                    files={"file": (path.name, handle, content_type)},
                )
        else:
            part_count = math.ceil(size / self.part_size)
            created = self._request(
                "POST",
                "/file_uploads",
                json={
                    "mode": "multi_part",
                    "filename": path.name,
                    "content_type": content_type,
                    "number_of_parts": part_count,
                },
            )
            upload_id = created["id"]
            with path.open("rb") as handle:
                for part_number in range(1, part_count + 1):
                    content = handle.read(self.part_size)
                    self._request(
                        "POST",
                        f"/file_uploads/{upload_id}/send",
                        data={"part_number": part_number},
                        files={"file": (path.name, content, content_type)},
                    )
            self._request("POST", f"/file_uploads/{upload_id}/complete")
        self._upload_cache[digest] = upload_id
        return upload_id


_MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
# Inline math: a single '$' pair on one line, not '$$' and not backslash-escaped.
_INLINE_MATH = re.compile(r"(?<!\\)\$(?!\$)([^\n$]+?)(?<!\\)\$(?!\$)")


def _rich_text_from_markdown(text: str) -> list[dict]:
    """Parse inline [label](url) and $math$ into typed Notion rich_text.

    - links become ``text.link`` segments (Notion reads them back as href)
    - inline math becomes an ``equation`` rich_text segment (NOT a block)
    - bare URLs, escaped \\$ and plain text stay untouched
    """
    tokens: list[tuple[int, int, dict]] = []
    for match in _MD_LINK.finditer(text):
        tokens.append((match.start(), match.end(), {
            "type": "text",
            "text": {"content": match.group(1)[:2000], "link": {"url": match.group(2)}},
        }))
    for match in _INLINE_MATH.finditer(text):
        tokens.append((match.start(), match.end(), {
            "type": "equation",
            "equation": {"expression": match.group(1).strip()[:2000]},
        }))
    tokens.sort(key=lambda item: item[0])
    # Drop overlaps: math inside a link label or vice versa keeps the first token.
    kept: list[tuple[int, int, dict]] = []
    for token in tokens:
        if kept and token[0] < kept[-1][1]:
            continue
        kept.append(token)

    segments: list[dict] = []
    cursor = 0
    for start, end, segment in kept:
        if start > cursor:
            segments.append({"type": "text", "text": {"content": text[cursor:start][:2000]}})
        segments.append(segment)
        cursor = end
    if cursor < len(text) or not segments:
        segments.append({"type": "text", "text": {"content": text[cursor:][:2000]}})
    return segments


def _text_block(block_type: str, text: str) -> dict:
    return {
        "object": "block",
        "type": block_type,
        block_type: {"rich_text": _rich_text_from_markdown(text)},
    }


def markdown_to_blocks(markdown: str, image_uploads: dict[str, str] | None = None) -> list[dict]:
    image_uploads = image_uploads or {}
    blocks: list[dict] = []
    in_frontmatter = False
    equation_lines: list[str] | None = None
    code_lines: list[str] | None = None
    for raw in markdown.splitlines():
        line = raw.strip()
        if code_lines is not None:
            if line.startswith("```"):
                blocks.append({
                    "object": "block", "type": "code",
                    "code": {"rich_text": [{"type": "text", "text": {"content": "\n".join(code_lines)[:2000]}}],
                             "language": "plain text"},
                })
                code_lines = None
            else:
                code_lines.append(raw)
            continue
        if equation_lines is not None:
            if line == "$$":
                expression = "\n".join(equation_lines)
                if not expression.strip():
                    raise ValueError("empty equation block")
                blocks.append({"object": "block", "type": "equation", "equation": {"expression": expression}})
                equation_lines = None
            else:
                equation_lines.append(raw)
            continue
        if line.startswith("```"):
            code_lines = []
            continue
        if line == "---" and not blocks:
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter or not line:
            continue
        if line == "$$":
            equation_lines = []
            continue
        image = IMAGE_LINE.match(line)
        if image and image.group(1) in image_uploads:
            blocks.append(
                {
                    "object": "block",
                    "type": "image",
                    "image": {"type": "file_upload", "file_upload": {"id": image_uploads[image.group(1)]}},
                }
            )
        elif line.startswith("### "):
            blocks.append(_text_block("heading_3", line[4:]))
        elif line.startswith("## "):
            blocks.append(_text_block("heading_2", line[3:]))
        elif line.startswith("# "):
            blocks.append(_text_block("heading_1", line[2:]))
        else:
            blocks.append(_text_block("paragraph", line))
    if code_lines is not None:
        blocks.append({
            "object": "block", "type": "code",
            "code": {"rich_text": [{"type": "text", "text": {"content": "\n".join(code_lines)[:2000]}}],
                     "language": "plain text"},
        })
    if equation_lines is not None:
        raise ValueError("unclosed equation block")
    return blocks


def publish_article(
    client,
    draft: ArticleDraft,
    database_id: str,
    *,
    write: bool = False,
    promote: bool = False,
    location: dict | None = None,
    metadata: dict | None = None,
    allow_overwrite: bool = False,
    skip_if_exists: bool = False,
    gate_stage: str = "publish",
) -> PublishResult:
    # Tiered gate: "publish" blocks truth gaps AND presentation defects;
    # "draft" blocks only truth gaps (presentation is advisory). Callers that
    # treat Notion as a draft sink (e.g. the review-package entry) pass
    # gate_stage="draft" so a non-HD figure does not block delivery.
    errors, _warnings = check_article(draft, stage=gate_stage)
    if errors:
        raise ValueError("article validation failed: " + "; ".join(errors))
    key = identityKey(draft)
    status = "Published" if promote else "Invisible"
    if not write:
        return PublishResult(draft.arxiv_id, "dry_run", status=status, identity_key=key)
    # Single write gate: a recognized, non-empty identity key. This replaces
    # the old arxiv-only guards in publish_article / materialize / review entry.
    if not canWriteSafely(draft):
        raise ValueError("paper identity required for write: no recognized identity key")
    if client is None:
        raise ValueError("Notion client is required for write mode")

    # Dedup on paper_key only -- one stable key for arXiv and ACL papers alike.
    existing = client.find_page_by_identity(database_id, key)
    properties = {
        "title": draft.title,
        "slug": draft.slug,
        "arxiv_id": draft.arxiv_id,
        "paper_key": key,
        "status": status,
    }
    # Everything the review package verified flows through verbatim: publication
    # date, authors, summary, year, venue, category, tags and the five geography
    # fields. Absent values are never written, so an empty field can no longer
    # erase an existing one.
    if metadata:
        for name, value in metadata.items():
            if value not in (None, "", [], {}):
                properties[name] = value
    # Five verified geography fields flow from the review package into Notion;
    # _properties() encodes them against the live schema and drops absent columns.
    if location:
        for name in LOCATION_FIELDS:
            if name in location and location[name] not in (None, ""):
                properties[name] = location[name]
    overwrite_snapshot = ""
    if existing:
        page_id = existing["id"]
        # Idempotent mode: the same paper (by identity key) already has a page
        # → report it and skip entirely, never touching existing content. This
        # is the user-facing "if id exists: already uploaded, do nothing" rule.
        if skip_if_exists:
            return PublishResult(draft.arxiv_id, "already_exists", page_id=page_id,
                                 status=status, identity_key=key)
        # P2 overwrite red line: snapshot the current body BEFORE clearing it,
        # and refuse to replace a non-empty page unless explicitly authorized.
        snapshot_result = client.retrieve_markdown(page_id) if hasattr(client, "retrieve_markdown") else {}
        overwrite_snapshot = str((snapshot_result or {}).get("markdown") or "")
        if overwrite_snapshot.strip() and not allow_overwrite:
            raise ValueError(
                "refusing to overwrite an existing Notion page with non-empty "
                "body; pass allow_overwrite=True to clear and replace it "
                "(pre-overwrite body was snapshotted)"
            )
        client.update_page(page_id, properties)
        action = "updated"
    else:
        page_id = client.create_page(database_id, properties)
        action = "created"

    image_uploads = {figure.path.name: client.upload_file(figure.path) for figure in draft.figures}
    blocks = markdown_to_blocks(draft.markdown, image_uploads)
    should_attach_pdf = bool(draft.source_pdf) and (
        existing is None or bool(existing.get("has_source_pdf"))
    )
    if should_attach_pdf:
        upload_id = client.upload_file(draft.source_pdf)
        blocks.append(
            {
                "object": "block",
                "type": "file",
                "file": {
                    "type": "file_upload",
                    "file_upload": {"id": upload_id},
                    "name": draft.source_pdf.name,
                },
            }
        )
    client.clear_children(page_id)
    for index in range(0, len(blocks), 100):
        client.append_children(page_id, blocks[index : index + 100])
    return PublishResult(draft.arxiv_id, action, page_id=page_id, status=status,
                         identity_key=key, overwrite_snapshot=overwrite_snapshot)
