#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一篇论文的写作准备：图注↔图片映射 + 出版元信息 + 代码仓库 + 素材摘要。

用法:
    python tools/prep_paper.py <data/parsed/论文目录> [--digest-out <文件>] [--title "英文标题"]

输出（紧凑，供写文章时直接看）:
  DIR / SIZE
  FIG    每张图的「文件名哈希 + 图注」（解析稿里图片引用后紧跟 Figure N: 图注）
  META   arXiv 的 published/updated（无 arXiv 则回退 OpenAlex 查 DOI + 日期）
  GH     解析稿里出现的 GitHub 链接
  DIGEST 写到 --digest-out（首部/章节/各节开头/数字/图注/主图描述）
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
UA = {"User-Agent": "recsys-blog-prep/1.0 (mailto:enkidulove90@gmail.com)"}
NS = {"a": "http://www.w3.org/2005/Atom"}


def biggest_md(d):
    mds = [x for x in glob.glob(os.path.join(d, "*.md")) if os.path.getsize(x) > 2000]
    if not mds:
        sys.exit(f"无解析稿 md: {d}")
    return max(mds, key=os.path.getsize)


def fig_map(md):
    """返回 [(image_hash, caption)]：图片引用后最近的 Figure 图注。"""
    L = open(md, encoding="utf-8").read().splitlines()
    last, out = None, []
    for ln in L:
        m = re.search(r"!\[\]\(images/([0-9a-f]+)\.(?:jpg|png)\)", ln)
        if m:
            last = m.group(1)
        c = re.match(r"^\s*(?:Figure|Fig\.?)\s*\d+[:.]?\s*(.+)$", ln)
        if c:
            out.append((last, re.sub(r"\s+", " ", c.group(1))[:150]))
    return out


def meta(title):
    """arXiv 优先，其次 OpenAlex。"""
    out = {}
    m = re.search(r"(\d{4}\.\d{4,5})", os.path.basename(os.path.abspath(FLAGS.dir)))
    if m:
        aid = m.group(1)
        try:
            u = f"https://export.arxiv.org/api/query?id_list={aid}"
            root = ET.fromstring(urllib.request.urlopen(
                urllib.request.Request(u, headers=UA), timeout=40).read())
            e = root.find("a:entry", NS)
            if e is not None:
                out["arxiv"] = aid
                out["date"] = e.find("a:published", NS).text[:10]
                out["updated"] = e.find("a:updated", NS).text[:10]
                out["title"] = " ".join(e.find("a:title", NS).text.split())
                return out
        except Exception as ex:
            out["arxiv_error"] = str(ex)
    q = urllib.parse.quote(title or "")
    if q:
        for u in (f"https://api.openalex.org/works?filter=title.search:{q}&per_page=3",
                  f"https://api.openalex.org/works?search={q}&per_page=3"):
            try:
                d = json.loads(urllib.request.urlopen(
                    urllib.request.Request(u, headers=UA), timeout=40).read())
            except Exception:
                continue
            for w in d.get("results", [])[:3]:
                pl = w.get("primary_location") or {}
                out.setdefault("openalex", []).append(
                    (w.get("publication_date"), w.get("doi"),
                     (w.get("title") or "")[:70], pl.get("landing_page_url")))
            if out.get("openalex"):
                break
    return out


def main():
    global FLAGS
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--digest-out", default="")
    ap.add_argument("--title", default="")
    FLAGS = ap.parse_args()
    d = FLAGS.dir
    md = biggest_md(d)
    print(f"DIR   {os.path.basename(d)}  ({os.path.getsize(md)//1024}KB)")
    print("FIG")
    for f, c in fig_map(md)[:12]:
        print(f"  [{f}] {c}")
    print("GH")
    t = open(md, encoding="utf-8").read()
    g = sorted({x.rstrip(".") for x in re.findall(r"https?://github\.com/[\w.\-]+/[\w.\-]+", t)})
    for x in (g or ["无"]):
        print("  " + x)
    print("META")
    mt = meta(FLAGS.title)
    for k, v in mt.items():
        print(f"  {k}: {v}")
    if FLAGS.digest_out:
        cmd = [sys.executable, os.path.join(HERE, "paper_digest.py"), d,
               "--out", FLAGS.digest_out, "--head-lines", "48", "--sec-lines", "4",
               "--max-num", "22"]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        print(f"DIGEST {FLAGS.digest_out} ({os.path.getsize(FLAGS.digest_out)//1024}KB)")


if __name__ == "__main__":
    main()
