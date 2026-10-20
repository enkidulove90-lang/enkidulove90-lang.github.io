#!/usr/bin/env python3
"""Plan and run a conservative Hexo-to-Notion content migration.

PDFs and parser work products are deliberately out of scope. The default mode
is a read-only inventory; ``--write`` is required for any Notion mutation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image

from notion_publish import NotionClient


FREE_FILE_LIMIT = 5 * 1024 * 1024
IMAGE_EXTENSIONS = {".avif", ".bmp", ".gif", ".heic", ".ico", ".jpeg", ".jpg", ".png", ".svg", ".tif", ".tiff", ".webp"}
IMAGE_PATTERN = re.compile(r"!\[([^]]*)\]\(([^)\s]+)(?:\s+['\"][^'\"]*['\"])?\)")


@dataclass(frozen=True)
class TextPart:
    markdown: str


@dataclass(frozen=True)
class ImagePart:
    path: Path
    caption: str
    source_reference: str
    sha256: str
    size: int


@dataclass(frozen=True)
class SkippedAsset:
    path: Path
    reason: str


@dataclass
class MigrationPost:
    path: Path
    title: str
    slug: str
    summary: str
    arxiv_id: str
    parts: list[TextPart | ImagePart] = field(default_factory=list)
    status: str = "Published"

    @property
    def images(self) -> list[ImagePart]:
        return [part for part in self.parts if isinstance(part, ImagePart)]


@dataclass(frozen=True)
class MigrationPlan:
    posts: list[MigrationPost]
    unique_assets: list[ImagePart]
    orphan_images: list[ImagePart]
    skipped: list[SkippedAsset]


@dataclass(frozen=True)
class MigrationResult:
    slug: str
    action: str
    page_id: str | None = None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _compress_raster(path: Path, cache_root: Path, max_file_bytes: int) -> Path | None:
    """Create a durable JPEG upload derivative without changing the source."""
    cache_root.mkdir(parents=True, exist_ok=True)
    target = cache_root / f"{_sha256(path)}.jpg"
    if target.is_file() and target.stat().st_size <= max_file_bytes:
        return target.resolve()
    try:
        with Image.open(path) as source:
            image = source.convert("RGB")
            for scale in (1.0, 0.85, 0.7, 0.55, 0.4, 0.3, 0.2, 0.12):
                if scale == 1.0:
                    candidate = image
                else:
                    candidate = image.resize(
                        (max(16, int(image.width * scale)), max(16, int(image.height * scale))),
                        Image.Resampling.LANCZOS,
                    )
                for quality in (92, 85, 75, 65, 50, 35):
                    candidate.save(target, "JPEG", quality=quality, optimize=True, progressive=True)
                    if target.stat().st_size <= max_file_bytes:
                        return target.resolve()
    except (OSError, ValueError):
        pass
    if target.exists():
        target.unlink()
    return None


def _upload_asset(
    path: Path,
    *,
    caption: str,
    source_reference: str,
    site_root: Path,
    max_file_bytes: int,
) -> ImagePart | None:
    upload_path = path.resolve()
    if upload_path.stat().st_size > max_file_bytes:
        upload_path = _compress_raster(
            upload_path,
            site_root / ".notion-migration-cache",
            max_file_bytes,
        )
        if upload_path is None:
            return None
    return ImagePart(
        path=upload_path,
        caption=caption,
        source_reference=source_reference,
        sha256=_sha256(upload_path),
        size=upload_path.stat().st_size,
    )


def _frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text
    values: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" not in line or line[:1].isspace():
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key.strip()] = value
    return values, text[end + 4 :].lstrip("\r\n")


def _resolve_image(reference: str, post_path: Path, site_root: Path) -> Path | None:
    if re.match(r"^(?:https?:)?//|^data:", reference, re.I):
        return None
    clean = reference.split("?", 1)[0].split("#", 1)[0]
    candidates = [
        site_root / "source" / clean.lstrip("/"),
        post_path.parent / clean,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def parse_post(path: Path, site_root: Path) -> MigrationPost:
    path = Path(path)
    site_root = Path(site_root)
    metadata, body = _frontmatter(path.read_text(encoding="utf-8", errors="replace"))
    parts: list[TextPart | ImagePart] = []
    cursor = 0
    for match in IMAGE_PATTERN.finditer(body):
        resolved = _resolve_image(match.group(2), path, site_root)
        if resolved is None:
            continue
        before = body[cursor : match.start()].strip()
        if before:
            parts.append(TextPart(before))
        parts.append(
            ImagePart(
                path=resolved,
                caption=match.group(1).strip() or resolved.stem,
                source_reference=match.group(2),
                sha256=_sha256(resolved),
                size=resolved.stat().st_size,
            )
        )
        cursor = match.end()
    tail = body[cursor:].strip()
    if tail:
        parts.append(TextPart(tail))
    if not parts:
        parts.append(TextPart(body.strip()))
    return MigrationPost(
        path=path.resolve(),
        title=metadata.get("title") or path.stem,
        slug=metadata.get("slug") or path.stem,
        summary=metadata.get("description", ""),
        arxiv_id=metadata.get("arxiv_id", ""),
        parts=parts,
    )


def build_migration_plan(site_root: Path, *, max_file_bytes: int = FREE_FILE_LIMIT) -> MigrationPlan:
    site_root = Path(site_root).resolve()
    posts = [parse_post(path, site_root) for path in sorted((site_root / "source" / "_posts").glob("*.md"))]
    skipped: list[SkippedAsset] = []
    referenced_paths: set[Path] = set()

    for post in posts:
        safe_parts: list[TextPart | ImagePart] = []
        for part in post.parts:
            if not isinstance(part, ImagePart):
                safe_parts.append(part)
                continue
            referenced_paths.add(part.path)
            asset = _upload_asset(
                part.path,
                caption=part.caption,
                source_reference=part.source_reference,
                site_root=site_root,
                max_file_bytes=max_file_bytes,
            )
            if asset is None:
                skipped.append(SkippedAsset(part.path, "over_limit"))
                safe_parts.append(TextPart(f"> 图片 `{part.path.name}` 超过 Notion 基础版限制，未迁移。"))
            else:
                safe_parts.append(asset)
        post.parts = safe_parts

    assets_by_hash: dict[str, ImagePart] = {}
    orphan_by_hash: dict[str, ImagePart] = {}
    images_root = site_root / "source" / "images"
    for image_path in sorted(path for path in images_root.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS):
        resolved = image_path.resolve()
        asset = _upload_asset(
            resolved,
            caption=resolved.stem,
            source_reference="/" + resolved.relative_to(site_root / "source").as_posix(),
            site_root=site_root,
            max_file_bytes=max_file_bytes,
        )
        if asset is None:
            if not any(item.path == resolved for item in skipped):
                skipped.append(SkippedAsset(resolved, "over_limit"))
            continue
        assets_by_hash.setdefault(asset.sha256, asset)
        if resolved not in referenced_paths:
            orphan_by_hash.setdefault(asset.sha256, asset)

    referenced_hashes = {image.sha256 for post in posts for image in post.images}
    orphan_images = [asset for digest, asset in orphan_by_hash.items() if digest not in referenced_hashes]
    return MigrationPlan(
        posts=posts,
        unique_assets=sorted(assets_by_hash.values(), key=lambda item: str(item.path)),
        orphan_images=sorted(orphan_images, key=lambda item: str(item.path)),
        skipped=sorted(skipped, key=lambda item: str(item.path)),
    )


def build_orphan_asset_posts(plan: MigrationPlan, *, group_size: int = 80) -> list[MigrationPost]:
    """Place otherwise-unreferenced site images on hidden Notion asset pages."""
    if group_size < 1:
        raise ValueError("group_size must be positive")
    posts: list[MigrationPost] = []
    for offset in range(0, len(plan.orphan_images), group_size):
        number = offset // group_size + 1
        images = plan.orphan_images[offset : offset + group_size]
        posts.append(
            MigrationPost(
                path=images[0].path,
                title=f"网站图片资产 {number:03d}",
                slug=f"notion-assets-{number:03d}",
                summary="由迁移工具保存的未直接嵌入文章的地图、城市或网站图片。",
                arxiv_id="",
                parts=[TextPart("此页面用于保存网站图片资产，请勿公开发布。"), *images],
                status="Invisible",
            )
        )
    return posts


def _notion_safe_markdown(markdown: str) -> str:
    """Escape ambiguous Markdown fragments that Notion otherwise consumes."""
    known_html = r"/?(?:table|tr|td|thead|tbody|sub|sup|br)\b"
    markdown = re.sub(
        rf"<(?!(?:{known_html}))(?=\s*(?:=|[A-Za-z0-9_]))",
        "`<`",
        markdown,
        flags=re.I,
    )
    markdown = re.sub(r"(?<=\|)\s*-{1,2}\s*(?=\|)", " — ", markdown)
    safe_lines = []
    for line in markdown.splitlines(keepends=True):
        if line.lstrip().startswith("|"):
            line = re.sub(r"\+(?=\s)", "`+`", line)
        safe_lines.append(line)
    return "".join(safe_lines)


def migrate_post(client, database_id: str, post: MigrationPost, *, write: bool = False) -> MigrationResult:
    if not write:
        return MigrationResult(post.slug, "dry_run")
    existing = client.find_page_by_slug(database_id, post.slug)
    properties = {
        "title": post.title,
        "slug": post.slug,
        "summary": post.summary,
        "arxiv_id": post.arxiv_id,
        "status": post.status,
    }
    if existing:
        page_id = existing["id"]
        client.update_page(page_id, properties)
        action = "updated"
    else:
        page_id = client.create_page(database_id, properties)
        action = "created"

    wrote_content = False
    for part in post.parts:
        if isinstance(part, TextPart):
            markdown = part.markdown.strip()
            if not markdown:
                continue
            if not wrote_content:
                client.replace_markdown(page_id, _notion_safe_markdown(markdown))
            else:
                client.append_markdown(page_id, _notion_safe_markdown(markdown))
            wrote_content = True
        else:
            if not wrote_content:
                client.replace_markdown(page_id, f"# {post.title}")
                wrote_content = True
            upload_id = client.upload_file(part.path)
            client.append_uploaded_image(page_id, upload_id, part.caption)
    if not wrote_content:
        client.replace_markdown(page_id, f"# {post.title}")
    return MigrationResult(post.slug, action, page_id)


def _load_env_file(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip().strip('"').strip("'")


def _report(plan: MigrationPlan, results: list[MigrationResult]) -> dict:
    return {
        "mode": "write" if any(item.action != "dry_run" for item in results) else "dry_run",
        "posts": len(plan.posts),
        "referenced_images": sum(len(post.images) for post in plan.posts),
        "unique_images": len(plan.unique_assets),
        "orphan_images": len(plan.orphan_images),
        "skipped": [
            {"path": str(item.path), "reason": item.reason}
            for item in plan.skipped
        ],
        "results": [item.__dict__ for item in results],
    }


def _select_posts(
    posts: list[MigrationPost],
    *,
    start_at: str | None,
    limit: int | None,
    slugs: list[str] | None,
) -> list[MigrationPost]:
    selected = posts
    if slugs:
        requested = set(slugs)
        known = {post.slug for post in posts}
        unknown = requested - known
        if unknown:
            raise ValueError("unknown --slug: " + ", ".join(sorted(unknown)))
        selected = [post for post in posts if post.slug in requested]
    if start_at:
        try:
            start = next(index for index, post in enumerate(posts) if post.slug == start_at)
        except StopIteration as exc:
            raise ValueError(f"unknown --start-at slug: {start_at}") from exc
        selected = posts[start:]
    return selected[:limit] if limit else selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--write", action="store_true", help="perform Notion writes; default is dry-run")
    parser.add_argument("--limit", type=int, help="migrate at most this many posts")
    parser.add_argument("--start-at", help="resume at this slug, including that item")
    parser.add_argument("--slug", action="append", dest="slugs", help="migrate only this slug; repeatable")
    parser.add_argument("--report", type=Path, default=Path("reports/notion-content-migration.json"))
    args = parser.parse_args()

    site_root = args.site_root.resolve()
    _load_env_file(site_root / ".env")
    _load_env_file(site_root / ".env.local")
    plan = build_migration_plan(site_root)
    all_posts = [*plan.posts, *build_orphan_asset_posts(plan)]
    try:
        posts = _select_posts(all_posts, start_at=args.start_at, limit=args.limit, slugs=args.slugs)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    client = None
    database_id = os.environ.get("NOTION_DATABASE_ID", "").strip()
    if args.write:
        token = os.environ.get("NOTION_TOKEN", "").strip()
        if not token or not database_id:
            raise SystemExit("--write requires NOTION_TOKEN and NOTION_DATABASE_ID")
        client = NotionClient(token)
    results = [migrate_post(client, database_id, post, write=args.write) for post in posts]
    report = _report(plan, results)
    report_path = args.report if args.report.is_absolute() else site_root / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key not in {"results", "skipped"}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
