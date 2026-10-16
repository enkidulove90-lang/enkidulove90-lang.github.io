#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""紧凑版写作素材（批量用）：一次给出 N 篇论文的「元信息 + 图注↔图片 + 摘要 +
章节 + 关键数字 + 结果表行」，控制每篇输出体积，便于一口气写多篇。

用法:
    python tools/mini_digest.py <dir1> <dir2> ...
"""
import glob
import html
import json
import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

NS = {"a": "http://www.w3.org/2005/Atom"}
UA = {"User-Agent": "recsys-blog/1.0 (mailto:enkidulove90@gmail.com)"}
ROWLIM, CELLLIM, CAPLIM = 8, 11, 8


def biggest_md(d):
    mds = [x for x in glob.glob(os.path.join(d, "*.md")) if os.path.getsize(x) > 2000]
    return max(mds, key=os.path.getsize) if mds else None


def clean(t):
    t = re.sub(r"<su[bp]>", "", t)
    t = re.sub(r"</su[bp]>", "", t)
    t = re.sub(r"\$[^$]{0,300}\$", " ⟨公式⟩ ", t)
    t = re.sub(r"\\(?:mathcal|text|mathbf|boldsymbol|mathbb|mathrm)\{[^}]*\}", "X", t)
    return re.sub(r"[ \t]+", " ", t)


def figmap(L):
    last, out = None, []
    for ln in L:
        m = re.search(r"!\[\]\(images/([0-9a-f]+)\.(?:jpg|png)\)", ln)
        if m:
            last = m.group(1)
        c = re.match(r"^\s*(?:Figure|Fig\.?)\s*\d+[:.]?\s*(.+)$", ln)
        if c:
            out.append((last, re.sub(r"\s+", " ", c.group(1))[:130]))
    return out


def tables(txt):
    res = []
    for tb in re.findall(r"<table>.*?</table>", txt, re.S):
        rows = []
        for tr in re.findall(r"<tr>(.*?)</tr>", tb, re.S):
            cells = [html.unescape(re.sub(r"<[^>]+>", " ", c)).strip()
                     for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
            cells = [re.sub(r"\s+", " ", c)[:26] for c in cells]
            if cells:
                rows.append(cells)
        if rows:
            res.append(rows)
    return res


def meta(d, title):
    out = {}
    m = re.search(r"(\d{4}\.\d{4,5})", os.path.basename(os.path.abspath(d)))
    if m:
        aid = m.group(1)
        try:
            u = f"https://export.arxiv.org/api/query?id_list={aid}"
            e = ET.fromstring(urllib.request.urlopen(
                urllib.request.Request(u, headers=UA), timeout=40).read()).find("a:entry", NS)
            if e is not None:
                out["arxiv"] = aid
                out["date"] = e.find("a:published", NS).text[:10]
                out["updated"] = e.find("a:updated", NS).text[:10]
                return out
        except Exception as ex:
            out["err"] = str(ex)[:60]
    q = urllib.parse.quote(title or "")
    if q:
        for u in (f"https://api.openalex.org/works?filter=title.search:{q}&per_page=2",
                  f"https://api.openalex.org/works?search={q}&per_page=2"):
            try:
                j = json.loads(urllib.request.urlopen(
                    urllib.request.Request(u, headers=UA), timeout=40).read())
            except Exception:
                continue
            for w in j.get("results", [])[:2]:
                out.setdefault("openalex", []).append(
                    (w.get("publication_date"), w.get("doi"), (w.get("title") or "")[:60]))
            if out.get("openalex"):
                break
    return out


def dump(d):
    md = biggest_md(d)
    if not md:
        print(f"!!! 无解析稿: {d}")
        return
    raw = open(md, encoding="utf-8").read()
    txt = clean(raw)
    L = txt.splitlines()
    print("=" * 90)
    print(f"@DIR {os.path.basename(d)}  ({os.path.getsize(md)//1024}KB)")
    h1 = next((x[2:].strip() for x in L if x.startswith("# ")), "")
    print(f"@TITLE {h1[:150]}")
    print("@META " + json.dumps(meta(d, h1), ensure_ascii=False)[:400])
    gh = sorted({x.rstrip(".") for x in re.findall(r"https?://github\.com/[\w.\-]+/[\w.\-]+", raw)})
    print("@GH " + (", ".join(gh[:2]) or "无"))
    print("@FIG")
    for f, c in figmap(L)[:CAPLIM]:
        print(f"  [{f}] {c}")
    # 摘要区
    ab = []
    for i, ln in enumerate(L):
        if re.match(r"^#+\s*(ABSTRACT|Abstract)", ln.strip()):
            ab = [x.strip() for x in L[i + 1:i + 14] if len(x.strip()) > 60]
            break
    if not ab:
        ab = [x.strip() for x in L[1:22] if len(x.strip()) > 90]
    print("@ABS " + " ".join(ab)[:1100])
    print("@HEAD " + " | ".join(x.strip()[:38] for x in L if re.match(r"^#{2,3}\s+\S", x))[:1500])
    # 关键数字句
    print("@NUM")
    pat = re.compile(r"(\d+\.\d+\s*%|0\.\d{3,}|outperform|improve[sd]?|relative|提升|优于|下降|降低)")
    n = 0
    for ln in L:
        s = ln.strip()
        if len(s) < 60 or s.startswith(("|", "#", "<")):
            continue
        if pat.search(s):
            print("  - " + s[:190])
            n += 1
            if n >= 16:
                break
    # 结果表
    print("@TABLE")
    for ti, tb in enumerate(tables(raw)[:3]):
        print(f"  -- table#{ti+1} ({len(tb)} rows)")
        for r in tb[:ROWLIM]:
            print("    " + " | ".join(r[:CELLLIM])[:210])


if __name__ == "__main__":
    for d in sys.argv[1:]:
        try:
            dump(d)
        except Exception as e:
            print(f"!!! {d}: {e}")
