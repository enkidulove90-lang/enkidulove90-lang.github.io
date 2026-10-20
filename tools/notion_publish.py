#!/usr/bin/env python3
"""Idempotently publish validated paper drafts to Notion."""

from __future__ import annotations

import hashlib
import math
import mimetypes
import re
import time
from dataclasses import dataclass
from pathlib import Path

import requests

from paper_article import ArticleDraft, validate_article


API = "https://api.notion.com/v1"
API_VERSION = "2026-03-11"
IMAGE_LINE = re.compile(r"^!\[[^]]*\]\(/images/papers/[^/]+/([^)]+)\)$")


@dataclass(frozen=True)
class PublishResult:
    arxiv_id: str
    action: str
    page_id: str | None = None
    status: str = "Invisible"


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
                self._property_names = set((source.get("properties") or {}).keys())
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
        if self._property_names is not None:
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


def _text_block(block_type: str, text: str) -> dict:
    return {
        "object": "block",
        "type": block_type,
        block_type: {"rich_text": [{"type": "text", "text": {"content": text[:2000]}}]},
    }


def markdown_to_blocks(markdown: str, image_uploads: dict[str, str] | None = None) -> list[dict]:
    image_uploads = image_uploads or {}
    blocks: list[dict] = []
    in_frontmatter = False
    for raw in markdown.splitlines():
        line = raw.strip()
        if line == "---" and not blocks:
            in_frontmatter = not in_frontmatter
            continue
        if in_frontmatter or not line:
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
    return blocks


def publish_article(
    client,
    draft: ArticleDraft,
    database_id: str,
    *,
    write: bool = False,
    promote: bool = False,
) -> PublishResult:
    errors = validate_article(draft)
    if errors:
        raise ValueError("article validation failed: " + "; ".join(errors))
    status = "Published" if promote else "Invisible"
    if not write:
        return PublishResult(draft.arxiv_id, "dry_run", status=status)
    if client is None:
        raise ValueError("Notion client is required for write mode")

    existing = client.find_page_by_arxiv(database_id, draft.arxiv_id)
    properties = {
        "title": draft.title,
        "slug": draft.slug,
        "summary": "",
        "arxiv_id": draft.arxiv_id,
        "status": status,
    }
    if existing:
        page_id = existing["id"]
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
    return PublishResult(draft.arxiv_id, action, page_id=page_id, status=status)
