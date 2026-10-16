#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一篇论文的解析稿压缩成「写作素材摘要」（digest），供人写深度文章时读。

用法:
    python tools/paper_digest.py <data/parsed/论文目录> [--out <文件>]

输出（控制在 ~12KB 内）:
  1. 首部原文（标题/作者/摘要区）
  2. 章节结构
  3. 每节开头若干行（看这节在讲什么）
  4. Markdown 表格（数据集/实验结果）
  5. 含数字/结论词的句子（实验数字来源）
  6. 图注全文 + figures.json 的主图描述（逐图解释的来源）

设计原则：**不替作者判断，只压缩**。写作时只用这里出现的信息，不要臆造。
"""
import argparse
import glob
import json
import os
import re
import sys


def pick_md(d):
    mds = [x for x in glob.glob(os.path.join(d, "*.md")) if os.path.getsize(x) > 3000]
    if not mds:
        sys.exit(f"目录里没有解析稿 md: {d}")
    return max(mds, key=os.path.getsize)


def load_figs(d):
    fs = glob.glob(os.path.join(d, "*_figures.json"))
    if not fs:
        return []
    try:
        j = json.load(open(fs[0], encoding="utf-8"))
    except Exception:
        return []
    return j.get("figures") or []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parsed_dir")
    ap.add_argument("--out")
    ap.add_argument("--head-lines", type=int, default=95)
    ap.add_argument("--sec-lines", type=int, default=7)
    ap.add_argument("--max-num", type=int, default=45)
    a = ap.parse_args()

    md = pick_md(a.parsed_dir)
    txt = open(md, encoding="utf-8").read()
    # MinerU 常把下标/上标 OCR 成 <sub>/<sup> 标签，把词切碎（"Y<sub>uec</sub>h<sub>e</sub>n<sub>g</sub>"）
    # 去掉标签后正好拼回原词，是净收益
    txt = re.sub(r"</?su[bp]>", "", txt)
    txt = re.sub(r"<[^>]{1,40}>", "", txt)
    lines = txt.splitlines()
    out = []
    add = out.append

    add(f"# DIGEST: {os.path.basename(a.parsed_dir.rstrip('/'))}")
    add(f"（源: {os.path.basename(md)}，{len(txt)//1024}KB / {len(lines)} 行）")
    add("")

    # 1. 首部原文（标题/作者/摘要）
    add("## 1. 首部原文（含摘要）")
    for ln in lines[:a.head_lines]:
        if ln.strip():
            add("  " + ln.rstrip()[:200])
    add("")

    # 2. 章节结构
    heads = [(i, ln.strip()) for i, ln in enumerate(lines)
             if re.match(r"^#{1,3}\s+\S", ln.strip())]
    add("## 2. 章节结构")
    for i, ln in heads:
        add(f"  L{i}: {ln[:110]}")
    add("")

    # 3. 每节开头若干行
    add("## 3. 各节开头（判断这节讲什么）")
    for k, (i, ln) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else min(i + 30, len(lines))
        seg = [x.strip() for x in lines[i + 1:end] if x.strip()]
        if not seg:
            continue
        add(f"### {ln[:90]}")
        for s in seg[:a.sec_lines]:
            add("  " + s[:190])
        add("")

    # 4. 表格
    add("## 4. 表格（数据集 / 实验结果）")
    seen = 0
    i = 0
    while i < len(lines) and seen < 6:
        if lines[i].strip().startswith("|") and i + 1 < len(lines) and set(lines[i + 1].replace("|", "").strip()) <= set("-: "):
            blk = []
            j = i
            while j < len(lines) and lines[j].strip().startswith("|"):
                blk.append(lines[j].strip()[:180])
                j += 1
            add(f"### 表 @L{i}（{len(blk)} 行）")
            for b in blk[:14]:
                add("  " + b)
            if len(blk) > 14:
                add(f"  …（余 {len(blk)-14} 行）")
            add("")
            seen += 1
            i = j
        else:
            i += 1

    # 5. 含数字的句子
    add("## 5. 含数字/结论词的句子（数字来源，勿臆造）")
    pat = re.compile(r"(\d+\.\d+\s*%|\d+\.\d{3,}|outperform|improve[sd]?|gain|boost|"
                     r"relative|absolute|SOTA|state-of-the-art|提升|优于|下降|drop)", re.I)
    got = 0
    for ln in lines:
        s = ln.strip()
        if len(s) < 40 or s.startswith("|") or s.startswith("#"):
            continue
        if pat.search(s):
            add("  - " + re.sub(r"\s+", " ", s)[:210])
            got += 1
            if got >= a.max_num:
                break
    add(f"（共命中 {got} 条）")
    add("")

    # 6. 图注
    add("## 6. 图注（解析稿内）")
    caps = re.findall(r"(?m)^(?:Figure|Fig\.?)\s*(\d+)[:.]?\s*(.+)$", txt)
    for n, c in caps[:24]:
        add(f"  Figure {n}: {re.sub(r'\\s+', ' ', c.strip())[:220]}")
    add("")

    # 7. 主图（figures.json）
    figs = load_figs(a.parsed_dir)
    add(f"## 7. 主图与视觉描述（figures.json，{len(figs)} 张）")
    for k, f in enumerate(figs):
        desc = re.sub(r"\s+", " ", (f.get("description") or ""))
        add(f"### 主图{k+1}  [{f.get('figure_type')}]  {f.get('image_file')}")
        add("  " + desc[:900])
        add("")

    text = "\n".join(out)
    if a.out:
        open(a.out, "w", encoding="utf-8", newline="\n").write(text)
        print(f"written {a.out} ({len(text)//1024}KB)")
    else:
        print(text)


if __name__ == "__main__":
    main()
