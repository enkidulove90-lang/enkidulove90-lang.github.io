#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 MinerU layout.json 的图块 bbox，从原始 PDF 渲染裁剪出完整配图（含矢量/拼贴图）。

用途：解析稿的 `images/` 里，**矢量绘制的图（tikz/pgfplots/多块拼贴）会被拆成几十个小位图**，
既拿不到完整图，文件名也与 md 引用对不上。此时按 layout.json 的 `para_blocks[].bbox`
（type=image / table）裁剪页面，能一次拿到完整图。

用法:
    python tools/crop_pdf_layout.py <layout.json> <origin.pdf> --out <目录> [--dpi 200] [--kinds image,table]

输出：每块一个 PNG（p<页>_<x>_<y>.png），并打印清单（含块类型、bbox、**配对到的 caption 文本**）：
    图块与其 y 方向最近的 caption 块配对，便于确认「这张图是 Figure 几」。
"""
import argparse
import json
import os
import sys

import pymupdf


def blocks_with_caption(pg):
    """返回 [(block, caption_text)]：caption 取同页 y 方向上最近的 caption 类块。"""
    blocks = pg.get("para_blocks") or []
    caps = [(b, "".join(
        s.get("content", "") for line in b.get("lines", []) for s in line.get("spans", [])
    ).strip()) for b in blocks if b.get("type") in ("image_caption", "table_caption", "caption")]
    out = []
    for b in blocks:
        bb = b.get("bbox")
        if not bb:
            continue
        cap = ""
        if caps:
            cy = bb[3]
            cand = [c for c in caps if c[0].get("bbox")]
            if cand:
                best = min(cand, key=lambda c: abs(c[0]["bbox"][1] - cy))
                cap = best[1]
        out.append((b, cap))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("layout_json")
    ap.add_argument("pdf")
    ap.add_argument("--out", required=True)
    ap.add_argument("--dpi", type=int, default=200)
    ap.add_argument("--kinds", default="image,table")
    ap.add_argument("--min-w", type=int, default=100)
    ap.add_argument("--min-h", type=int, default=60)
    a = ap.parse_args()
    kinds = set(a.kinds.split(","))

    os.makedirs(a.out, exist_ok=True)
    j = json.load(open(a.layout_json, encoding="utf-8"))
    doc = pymupdf.open(a.pdf)
    print("页 | 类型 | bbox | 文件 | 配对图注")
    for pg in j.get("pdf_info", []):
        idx = pg.get("page_idx", 0)
        if idx >= len(doc):
            continue
        page = doc[idx]
        for b, cap in blocks_with_caption(pg):
            if b.get("type") not in kinds:
                continue
            bb = b.get("bbox")
            if not bb:
                continue
            rect = pymupdf.Rect(*bb)
            if rect.width < a.min_w or rect.height < a.min_h:
                continue
            r = pymupdf.Rect(rect.x0, rect.y0, rect.x1, rect.y1)
            if r.y1 > page.rect.height or r.x1 > page.rect.width:
                r = r & page.rect
            try:
                pix = page.get_pixmap(clip=r, dpi=a.dpi)
            except Exception as e:
                print(f"  p{idx+1} 裁剪失败: {e}", file=sys.stderr)
                continue
            fn = f"p{idx+1}_{int(bb[0])}_{int(bb[1])}.png"
            pix.save(os.path.join(a.out, fn))
            print(f"  p{idx+1:>3} | {b.get('type'):<13} | {[round(x) for x in bb]} | {fn} | {cap[:110]}")


if __name__ == "__main__":
    main()
