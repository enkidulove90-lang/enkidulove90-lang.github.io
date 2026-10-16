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


def slugify(title, page_id):
    s = re.sub(r"[\\/:*?\"<>|\s]+", "-", title.strip()).strip("-")
    s = urllib.parse.quote(s)[:60] if not re.fullmatch(r"[A-Za-z0-9._-]+", s) else s[:60]
    return (s or "post") + "-" + page_id.replace("-", "")[:8]


def download(url, name):
    """下载图片到 source/images/，返回本地相对路径。"""
    os.makedirs(IMAGES, exist_ok=True)
    path = os.path.join(IMAGES, name)
    if not os.path.exists(path):  # 增量：已下载过的不重复拉
        rr = requests.get(url, timeout=120)
        rr.raise_for_status()
        with open(path, "wb") as f:
            f.write(rr.content)
    return "/images/" + name


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
        if src.startswith("https://prod-files-secure") or "notion.so" in urllib.parse.urlparse(src).netloc:
            name = hashlib.md5(src.encode()).hexdigest() + ".png"
            try:
                src = download(src, name)
            except Exception as e:
                print(f"  ! image download failed: {e}", file=sys.stderr)
        lines.append(f"![]({src})")
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


def page_to_md(page):
    props = page["properties"]
    title = plain(props["title"]["title"]) if "title" in props else plain(props["Title"]["title"])
    tags = [plain(t["name"]) for t in props["tags"]["multi_select"]]
    category = plain(props["category"]["select"]["name"]) if props["category"]["select"] else "未分类"
    slug = plain(props["slug"]["rich_text"]) or slugify(title, page["id"])
    summary = plain(props["summary"]["rich_text"])
    date = (page["properties"]["date"]["date"] or {}).get("start", page["created_time"][:10])

    md = ["---", f"title: {title}", f"date: {date}", f"categories: [{category}]",
          f"tags: [{', '.join(tags)}]"]
    if slug:
        md.append(f"slug: {slug}")
    if summary:
        md.append(f"description: {summary}")
    md.append("---", )
    body = blocks_children(page["id"])
    md.extend(block_to_md(b) for b in body)
    return "\n\n".join(md) + "\n"


def main():
    # 未配置 Secrets 时优雅跳过，保证站点仍能正常构建
    if not TOKEN or not DB:
        print("notion sync skipped: NOTION_TOKEN / NOTION_DATABASE_ID not set", file=sys.stderr)
        return 0
    os.makedirs(POSTS, exist_ok=True)
    state = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
    pq = {"property": "status", "select": {"equals": "Published"}}  # 若 status 是 checkbox 改见 README
    pt = {"property": "type", "select": {"equals": "Post"}}
    body = {"filter": {"and": [pq, pt]}, "sorts": [{"property": "date", "direction": "descending"}]}
    n_new = n_skip = 0
    cur = None
    while True:
        if cur:
            body["start_cursor"] = cur
        d = api("POST", f"/databases/{DB}/query", json=body)
        for page in d.get("results", []):
            pid = page["id"]
            edited = page["last_edited_time"]
            if state.get(pid) == edited:
                n_skip += 1
                continue
            try:
                md = page_to_md(page)
                title = re.search(r"title: (.+)", md).group(1)
                fn = slugify(title, pid) + ".md"
                open(os.path.join(POSTS, fn), "w", encoding="utf-8").write(md)
                state[pid] = edited
                n_new += 1
                print(f"  + {title}")
            except Exception as e:
                print(f"  ! {pid} failed: {e}", file=sys.stderr)
            time.sleep(0.34)
        if not d.get("has_more"):
            break
        cur = d.get("next_cursor")
    json.dump(state, open(STATE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"sync done: {n_new} updated, {n_skip} unchanged")


if __name__ == "__main__":
    main()
