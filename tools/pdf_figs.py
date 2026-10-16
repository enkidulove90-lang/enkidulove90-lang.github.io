#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从论文 PDF 提取「大图 + 图注」配对清单，并把图导出为 PNG。

用途：当 MinerU 解析稿的 `images/` 文件名与 md 里的引用哈希对不上（或干脆没有独立图片文件）时，
直接从 PDF 内嵌位图取原图，并用「图片在页面上的 y 区间 + 页内 Figure 图注的 y 位置」配对，
确定每张图到底是什么图。

用法:
    python tools/pdf_figs.py <pdf> --out <目录> [--min-px 200] [--lang both]

输出：每张图一个 PNG（文件名 p<页>_<序号>_<尺寸>.png），并打印清单：
    页 | 尺寸 | y区间 | 配对的图注（截断）
"""
import argparse
import os
import re
import sys

import pymupdf

CAP = re.compile(r"(?:Figure|Fig\.?)\s*(\d+)\s*[:.]|图\s*(\d+)\s*[:.]", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--out", required=True)
    ap.add_argument("--min-px", type=int, default=200, help="小于该边长的图视为 logo/分隔线，跳过")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    doc = pymupdf.open(a.pdf)
    rows = []
    for pno, page in enumerate(doc):
        # 页内图注 (文本, y) —— 用搜索拿位置
        caps = []
        for m in re.finditer(r"(?:Figure|Fig\.?)\s*\d+\s*[:.]|图\s*\d+\s*[:.]", page.get_text()):
            pass
        for txt in re.findall(r"^(?:Figure|Fig\.?)\s*\d+\s*[:.].{0,160}|^图\s*\d+\s*[:.].{0,160}",
                              page.get_text(), re.M):
            hits = page.search_for(txt.strip()[:60])
            if hits:
                caps.append((round(hits[0].y0), re.sub(r"\s+", " ", txt.strip())))
        for j, info in enumerate(page.get_images(full=True)):
            xref = info[0]
            try:
                pix = pymupdf.Pixmap(doc, xref)
            except Exception as e:  # 内嵌图损坏
                print(f"  ! p{pno+1} #{j} 读取失败: {e}", file=sys.stderr)
                continue
            w, h = pix.width, pix.height
            if w < a.min_px or h < a.min_px:
                continue
            if pix.n > 4:
                pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
            fn = f"p{pno+1}_{j}_{w}x{h}.png"
            path = os.path.join(a.out, fn)
            pix.save(path)
            rects = page.get_image_rects(xref)
            y0, y1 = (round(rects[0].y0), round(rects[0].y1)) if rects else (None, None)
            # 配对：取与该图 y 区间距离最近的图注
            best = ""
            if y0 is not None and caps:
                best = min(caps, key=lambda c: abs(c[0] - y1 if c[0] > y1 else abs(c[0] - y0)))[1]
            rows.append((pno + 1, fn, w, h, y0, y1, best))
    print("\n页 | 文件 | 尺寸 | y区间 | 图注")
    for r in rows:
        print(f"  p{r[0]:>3} | {r[1]:<24} | {r[2]}x{r[3]} | {r[4]}-{r[5]} | {r[6][:110]}")


if __name__ == "__main__":
    main()
