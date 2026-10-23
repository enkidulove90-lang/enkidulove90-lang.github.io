#!/usr/bin/env python3
"""Notion 数据库 -> Hexo Markdown 增量同步。

- 读取环境变量 NOTION_TOKEN / NOTION_DATABASE_ID
- 只取 status=Published 且 type=Post 的条目
- 字段映射：title/slug/summary/date/category/tags
- 图片：Notion 文件签名 URL 约 1 小时过期 -> 一律下载进 source/images/
- 增量：.notion_state.json 记录 last_edited_time，只重写变更条目
- 限速：Notion API 3 req/s
"""
import base64
import hashlib
import json
import os
import re
import sys
import time
import urllib.parse

import requests

API = "https://api.notion.com/v1"
VER = "2022-06-28"
TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DB = os.environ.get("NOTION_DATABASE_ID", "").strip()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "source", "_posts")
IMAGES = os.path.join(ROOT, "source", "images")
PAPERS = os.path.join(ROOT, "source", "papers")
STATE = os.path.join(ROOT, "tools", ".notion_state.json")
H = {"Authorization": f"Bearer {TOKEN}", "Notion-Version": VER, "Content-Type": "application/json"}


def api(method, path, **kw):
    for attempt in range(5):
        r = requests.request(method, API + path, headers=H, timeout=60, **kw)
        if r.status_code == 429:
            time.sleep(float(r.headers.get("Retry-After", 1)))
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError("Notion API retry exhausted")


def plain(rich):
    return "".join(seg.get("plain_text", "") for seg in rich)


def notion_text_property(props, name):
    """Read a city-like Notion property whether it is Text or Select."""
    prop = props.get(name) or {}
    selected = prop.get("select") or {}
    return (selected.get("name") or plain(prop.get("rich_text", []))).strip()


def notion_city_list(props, name):
    """Read cities from Multi-select, Select, or comma-separated Text."""
    prop = props.get(name) or {}
    selected = [item.get("name", "").strip() for item in prop.get("multi_select", [])]
    if not selected:
        scalar = notion_text_property(props, name)
        selected = [item.strip() for item in re.split(r"[,，、;；]", scalar) if item.strip()]
    return list(dict.fromkeys(item for item in selected if item))


def notion_location_fields(props):
    """Normalize the five Notion geography properties used by the map pipeline."""
    return {
        "location_type": notion_text_property(props, "location_type"),
        "venue_city": notion_text_property(props, "venue_city"),
        "affil_city": notion_city_list(props, "affil_city"),
        "corresponding_city": notion_text_property(props, "corresponding_city"),
        "affiliation_name": notion_text_property(props, "affiliation_name"),
    }


def slugify(title, page_id):
    s = re.sub(r"[\\/:*?\"<>|\s]+", "-", title.strip()).strip("-")
    s = urllib.parse.quote(s)[:60] if not re.fullmatch(r"[A-Za-z0-9._-]+", s) else s[:60]
    return (s or "post") + "-" + page_id.replace("-", "")[:8]


def page_slug(page):
    """Use the curated Notion slug as the canonical post filename."""
    props = page["properties"]
    title = plain((props.get("title") or props.get("Title") or {}).get("title", []))
    configured = plain((props.get("slug") or {}).get("rich_text", [])).strip()
    if configured and re.fullmatch(r"[A-Za-z0-9._-]+", configured):
        return configured
    return slugify(title, page["id"])


def download_to(url, name, destination, public_prefix):
    """下载 Notion 临时文件到稳定的站点目录。"""
    os.makedirs(destination, exist_ok=True)
    name = os.path.basename(name)
    path = os.path.join(destination, name)
    if not os.path.exists(path):  # 增量：已下载过的不重复拉
        rr = requests.get(url, timeout=120)
        rr.raise_for_status()
        with open(path, "wb") as f:
            f.write(rr.content)
    return public_prefix.rstrip("/") + "/" + name


def download(url, name):
    """下载图片到 source/images/，返回本地相对路径。"""
    return download_to(url, name, IMAGES, "/images")


def blocks_rich_to_md(rich):
    out = ""
    for seg in rich:
        t = seg.get("plain_text", "")
        ann = seg.get("annotations", {})
        if ann.get("code"):
            t = f"`{t}`"
        if ann.get("bold"):
            t = f"**{t}**"
        if ann.get("italic"):
            t = f"*{t}*"
        href = seg.get("href")
        if href:
            t = f"[{t}]({href})"
        out += t
    return out


def block_to_md(b):
    """单个 Notion block -> Markdown 片段（递归子块）。"""
    t = b["type"]
    v = b.get(t, {})
    txt = blocks_rich_to_md(v.get("rich_text", []))
    lines = []
    if t == "paragraph":
        if txt:
            lines.append(txt)
    elif t in ("heading_1", "heading_2", "heading_3"):
        lines.append("#" * int(t[-1]) + " " + txt)
    elif t == "bulleted_list_item":
        lines.append("- " + txt)
    elif t == "numbered_list_item":
        lines.append("1. " + txt)
    elif t == "quote":
        lines.append("> " + txt)
    elif t == "code":
        lines.append(f"```{v.get('language','')}\n{txt}\n```")
    elif t == "divider":
        lines.append("---")
    elif t == "image":
        src = v.get("file", {}).get("url") or (v.get("external", {}).get("url") or "")
        alt = blocks_rich_to_md(v.get("caption", []))
        if src.startswith("https://prod-files-secure") or "notion.so" in urllib.parse.urlparse(src).netloc:
            name = hashlib.md5(src.encode()).hexdigest() + ".png"
            try:
                src = download(src, name)
            except Exception as e:
                print(f"  ! image download failed: {e}", file=sys.stderr)
        lines.append(f"![{alt}]({src})")
    elif t == "file":
        src = v.get("file", {}).get("url") or (v.get("external", {}).get("url") or "")
        name = os.path.basename(v.get("name") or urllib.parse.urlparse(src).path) or "paper.pdf"
        if src.startswith("https://prod-files-secure") or "notion.so" in urllib.parse.urlparse(src).netloc:
            try:
                src = download_to(src, name, PAPERS, "/papers")
            except Exception as e:
                print(f"  ! file download failed: {e}", file=sys.stderr)
        lines.append(f"[{name}]({src})")
    elif t == "bookmark" or t == "link_preview":
        lines.append(v.get("url", ""))
    elif t == "child_page":
        lines.append(f"### {v.get('title','')}")
    # 递归有子块的类型
    if b.get("has_children") and t not in ("child_page",):
        sub = blocks_children(b["id"])
        lines.extend(block_to_md(c) for c in sub)
    return "\n".join(lines)


def blocks_children(block_id):
    out, cur = [], None
    while True:
        params = {"page_size": 100}
        if cur:
            params["start_cursor"] = cur
        d = api("GET", f"/blocks/{block_id}/children", params=params)
        out.extend(d.get("results", []))
        if not d.get("has_more"):
            break
        cur = d.get("next_cursor")
        time.sleep(0.34)
    return out


def frontmatter_categories(path):
    """Read an existing Hexo category list without requiring a YAML dependency."""
    if not path or not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as handle:
        match = re.search(r"^categories:\s*\[(.*?)\]\s*$", handle.read(), re.MULTILINE)
    if not match:
        return []
    values = [item.strip().strip('"\'') for item in match.group(1).split(",")]
    return [item for item in values if item and item != "未分类"]


def frontmatter_date(path):
    """Read a previously verified paper date so an incomplete Notion page cannot erase it."""
    if not path or not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as handle:
        match = re.search(r"^date:\s*[\"']?(\d{4}-\d{2}-\d{2})[\"']?\s*$", handle.read(), re.MULTILINE)
    return match.group(1) if match else ""


def page_to_md(page, fallback_categories=None, fallback_date=""):
    props = page["properties"]
    title = plain((props.get("title") or props.get("Title") or {}).get("title", []))
    if not title:
        raise ValueError("标题为空，已跳过（请在 Notion 里填上 title）")
    tags = [t.get("name", "") for t in (props.get("tags") or {}).get("multi_select", [])]
    sel = (props.get("category") or {}).get("select") or {}
    category = sel.get("name")
    slug = page_slug(page)
    summary = plain((props.get("summary") or {}).get("rich_text", []))
    notion_date = ((props.get("date") or {}).get("date") or {}).get("start")
    published = plain((props.get("published") or {}).get("rich_text", []))
    date = notion_date or published[:10] or fallback_date or page["created_time"][:10]

    # 多维筛选字段（与「分类」正交的三个独立维度，供前端 Tabs 过滤器使用）：
    #   year        Select   发布/出版年
    #   venue_type  Select   会议 / 期刊 / arXiv预印本
    #   venue_name  Text     具体会议或期刊简称（如 SIGIR 2025、ACM TORS）
    year = ((props.get("year") or {}).get("select") or {}).get("name") or str(date)[:4]
    venue_type = ((props.get("venue_type") or {}).get("select") or {}).get("name") or "arXiv预印本"
    venue_name = plain((props.get("venue_name") or {}).get("rich_text", []))
    arxiv_id = plain((props.get("arxiv_id") or {}).get("rich_text", []))
    location = notion_location_fields(props)

    # 三维分类落地：Notion 的 category 写「领域大类 / 二级分类」（斜杠或逗号分隔），
    # tags 放「任务场景 + 技术方法」；Hexo 侧 categories 支持两级、tags 为标签云
    cats = [x.strip() for x in re.split(r"[,/、]", category or "") if x.strip()]
    if not cats:
        cats = list(fallback_categories or []) or ["未分类"]
    tags = list(dict.fromkeys(["论文速读"] + tags))
    md = ["---", "title: " + json.dumps(title, ensure_ascii=False),
          "date: " + json.dumps(str(date), ensure_ascii=False),
          "year: " + json.dumps(str(year), ensure_ascii=False),
          "venue_type: " + json.dumps(venue_type, ensure_ascii=False),
          "venue_name: " + (json.dumps(venue_name, ensure_ascii=False) if venue_name else '""'),
          "categories: " + json.dumps(cats, ensure_ascii=False),
          "tags: " + json.dumps(tags, ensure_ascii=False)]
    if slug:
        md.append("slug: " + json.dumps(slug, ensure_ascii=False))
    if summary:
        md.append("description: " + json.dumps(summary, ensure_ascii=False))
    if arxiv_id:
        md.append("arxiv_id: " + json.dumps(arxiv_id, ensure_ascii=False))
    for field in ("location_type", "venue_city", "affil_city", "corresponding_city", "affiliation_name"):
        value = location[field]
        if value:
            md.append(field + ": " + json.dumps(value, ensure_ascii=False))
    # 封面不写死：交给主题的 cover.default_cover 池在每次构建时随机分配
    # （池内是固定 seed 图，有 30 天 immutable 缓存，不影响加载速度）
    md.append("---", )
    body = blocks_children(page["id"])
    md.extend(block_to_md(b) for b in body)
    return "\n\n".join(md) + "\n"


def preserve_existing_post_when_remote_body_is_empty(generated_md, destination):
    """Do not replace a complete local essay with an empty Notion page."""
    generated_parts = generated_md.split("---", 2)
    generated_body = generated_parts[2].strip() if len(generated_parts) == 3 else ""
    if generated_body or not os.path.exists(destination):
        return generated_md
    with open(destination, encoding="utf-8") as handle:
        existing_md = handle.read()
    existing_parts = existing_md.split("---", 2)
    existing_body = existing_parts[2].strip() if len(existing_parts) == 3 else ""
    return existing_md if existing_body else generated_md


def published_posts_query():
    """Return a fresh query that makes Draft pages impossible to sync."""
    return {
        "filter": {
            "and": [
                {"property": "status", "select": {"equals": "Published"}},
                {"property": "type", "select": {"equals": "Post"}},
            ]
        },
        "sorts": [{"property": "date", "direction": "descending"}],
    }


def is_published_post(page):
    props = page.get("properties") or {}
    status = ((props.get("status") or {}).get("select") or {}).get("name")
    content_type = ((props.get("type") or {}).get("select") or {}).get("name")
    return status == "Published" and content_type == "Post"


def validate_unique_page_slugs(pages):
    """Reject ambiguous identities before any Markdown file can be overwritten."""
    owners = {}
    for page in pages:
        slug = page_slug(page)
        previous = owners.get(slug)
        if previous and previous != page["id"]:
            raise ValueError(
                f"slug collision: {slug} resolves from both {previous} and {page['id']}"
            )
        owners[slug] = page["id"]


def can_skip_unchanged_page(page, state, destination):
    """A timestamp cache hit is valid only while its materialized file exists."""
    return (
        state.get(page["id"]) == page["last_edited_time"]
        and os.path.isfile(destination)
    )


def iter_published_pages(page_id=""):
    """Yield one intake page when provided, otherwise reconcile database metadata."""
    if page_id:
        page = api("GET", f"/pages/{page_id}")
        if not is_published_post(page):
            raise ValueError(f"target page is not Published + Post: {page_id}")
        yield page
        return
    body = published_posts_query()
    cursor = None
    pages = []
    while True:
        if cursor:
            body["start_cursor"] = cursor
        data = api("POST", f"/databases/{DB}/query", json=body)
        pages.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    validate_unique_page_slugs(pages)
    yield from pages


def main():
    # 未配置 Secrets 时优雅跳过，保证站点仍能正常构建
    if not TOKEN or not DB:
        print("notion sync skipped: NOTION_TOKEN / NOTION_DATABASE_ID not set", file=sys.stderr)
        return 0
    os.makedirs(POSTS, exist_ok=True)
    state = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
    target_page_id = os.environ.get("NOTION_PAGE_ID", "").strip()
    n_new = n_skip = 0
    for page in iter_published_pages(target_page_id):
        pid = page["id"]
        edited = page["last_edited_time"]
        fn = page_slug(page) + ".md"
        destination = os.path.join(POSTS, fn)
        if can_skip_unchanged_page(page, state, destination):
            n_skip += 1
            continue
        try:
            md = page_to_md(
                page,
                fallback_categories=frontmatter_categories(destination),
                fallback_date=frontmatter_date(destination),
            )
            title = re.search(r"title: (.+)", md).group(1)
            md = preserve_existing_post_when_remote_body_is_empty(md, destination)
            open(destination, "w", encoding="utf-8").write(md)
            state[pid] = edited
            n_new += 1
            print(f"  + {title}")
        except Exception as e:
            print(f"  ! {pid} failed: {e}", file=sys.stderr)
        time.sleep(0.34)
    json.dump(state, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"sync done: {n_new} updated, {n_skip} unchanged")
    if n_new + n_skip == 0:
        print("warn: 查询命中 0 条 —— 检查 status 是否正好是 Published、type 是否正好是 Post，"
              "以及该数据库是否已 Connect 到这个 integration", file=sys.stderr)


if __name__ == "__main__":
    main()
