#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把一段手写的正文组装成 Hexo 文章（front matter + 论文/代码出处行 + 正文）。

用法:
    python tools/assemble_post.py --slug recgoat-dual-semantic-alignment \
        --title "标题" --category "多模态推荐" --tags "多模态,最优传输" \
        --date 2026-01-31 [--updated 2026-05-25] \
        [--arxiv 2602.00682] [--github https://github.com/x/y] \
        --body <正文 md> [--description "列表摘要"] [--force]

设计要点:
  - 出处行由脚本统一生成，避免"忘记加链接"（踩过：手写正文漏掉 `> 论文：…`）
  - 默认跳过已存在的文章，需 --force 才覆盖（手工精修过的不能被冲掉）
  - front matter 的 title/description 用 json.dumps 转义，避免标点破坏 YAML
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "source", "_posts")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--category", required=True)
    ap.add_argument("--tags", default="")
    ap.add_argument("--date", required=True, help="论文真实首次发布日 YYYY-MM-DD")
    ap.add_argument("--updated", default="")
    ap.add_argument("--arxiv", default="")
    ap.add_argument("--doi", default="", help="无 arXiv 版时用 DOI 链接（ACM/IEEE/期刊）")
    ap.add_argument("--github", default="")
    ap.add_argument("--body", required=True)
    ap.add_argument("--description", default="")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    body = open(a.body, encoding="utf-8").read().lstrip("\n").rstrip() + "\n"
    fm = ["---", "title: " + json.dumps(a.title, ensure_ascii=False), "date: " + a.date]
    if a.updated:
        fm.append("updated: " + a.updated)
    fm.append("categories: [" + ", ".join(
        [x.strip() for x in re.split(r"[,/、]", a.category) if x.strip()]) + "]")
    tags = [t.strip() for t in a.tags.split(",") if t.strip()]
    tags = list(dict.fromkeys(["论文速读"] + tags))   # 全局标签，供导航「论文速递」入口
    if tags:
        fm.append("tags: [" + ", ".join(tags) + "]")
    fm.append("slug: " + a.slug)
    if a.description:
        fm.append("description: " + json.dumps(a.description, ensure_ascii=False))
    fm.append("---")

    links = []
    if a.arxiv:
        links.append(f"论文：[arXiv {a.arxiv}](https://arxiv.org/abs/{a.arxiv})")
    elif a.doi:
        links.append(f"论文：[DOI]({a.doi})")
    if a.github:
        links.append(f"代码：[GitHub]({a.github})")
    head = ("> " + " · ".join(links) + "\n\n") if links else ""

    post = "\n".join(fm) + "\n\n" + head + body
    out = os.path.join(POSTS, a.slug + ".md")
    if os.path.exists(out) and not a.force:
        sys.exit(f"已存在，跳过（需 --force 覆盖）: {out}")
    if a.dry_run:
        print(f"[dry-run] 将写入 {out} ({len(post)}B)")
        print(post[:400])
        return
    os.makedirs(POSTS, exist_ok=True)
    open(out, "w", encoding="utf-8", newline="\n").write(post)
    print(f"written {out} ({len(post)}B)")


if __name__ == "__main__":
    main()
