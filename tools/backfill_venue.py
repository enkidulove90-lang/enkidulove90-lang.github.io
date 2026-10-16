#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为已发布文章回填 front matter 的三个多维筛选字段：year / venue_type / venue_name。

判定原则（宁缺勿错）：
  1. 证据优先级：arXiv `comment`（"Accepted by X"）> arXiv `journal_ref` > DOI 的 OpenAlex 记录（type + source）
  2. 无上述证据 → venue_type = "arXiv预印本"，venue_name = "arXiv"
  3. venue_type 只取三值：会议 / 期刊 / arXiv预印本
  4. year 取**出版年**（会议/期刊年份）；预印本取 arXiv 发布年（与文章 date 一致）

用法:
    python tools/backfill_venue.py <posts_dir> [--apply]     # 默认 dry-run
"""
import argparse
import glob
import os
import re
import sys

# slug -> (venue_type, venue_name, year, 依据)
RULE = {
    # —— 会议（证据：arXiv comment 明确 Accepted）——
    "adaptive-kg-retriever": ("会议", "ACL 2026", 2026, "comment: Accepted at ACL 2026 Main Conference"),
    "cammsr-category-guided-moe-seqrec": ("会议", "ICDE 2026", 2026, "comment: Accepted by ICDE 2026"),
    "earn-register-token-inference-accel": ("会议", "KDD 2025", 2025, "comment: Accepted by KDD 2025"),
    "graph-r1-agentic-graphrag-rl": ("会议", "ICML 2026", 2026, "comment: Accepted by ICML 2026 + journal_ref"),
    "i3mrec-invariant-information-bottleneck": ("会议", "ACM MM 2025", 2025, "comment: ACM Multimedia 2025 Accepted"),
    "lightgcl-svd-contrastive-view": ("会议", "ICLR 2023", 2023, "comment: ICLR 2023"),
    "llm-denoising-recommendation": ("会议", "WWW 2025", 2025, "comment: Accepted by WWW 2025"),
    "m3bsr-multimodal-multibehavior-diffusion": ("会议", "SIGIR 2025", 2025, "comment+journal_ref: SIGIR 2025"),
    "mixragrec-moe-kg-retrieval": ("会议", "KDD 2026", 2026, "comment: Accepted by KDD 2026 Research Track"),
    "mmsr-adaptive-multimodal-fusion": ("会议", "CIKM 2023", 2023, "comment: CIKM 2023"),
    "mmssl-multimodal-self-supervised": ("会议", "WWW 2023", 2023, "comment: published as full paper at WWW 2023"),
    "nlgcl-neighbor-layer-contrastive": ("会议", "RecSys 2025", 2025, "comment: Accepted by RecSys 2025 Spotlight Oral"),
    "reclm-recommendation-instruction-tuning": ("会议", "ACL 2025", 2025, "comment: accepted by ACL 2025 main conference"),
    "smore-spectrum-modality-fusion": ("会议", "WSDM 2025", 2025, "comment: Accepted to WSDM 2025"),
    # —— 会议（证据：DOI 的 OpenAlex 记录 type=conference-paper）——
    "prism-information-synergy-module": ("会议", "WWW 2026", 2026, "DOI 10.1145/3774904.3792230 -> ACM Web Conference (WWW)"),
    "msca-multi-view-semantic-alignment": ("会议", "WWW 2026", 2026, "DOI 10.1145/3774904.3792192 -> WWW'26"),
    "mmgcf-graph-collaborative-filtering": ("会议", "UMAP 2026", 2026, "DOI 10.1145/3774935.3806158 -> ACM UMAP"),
    "mamex-moe-coldstart-recommendation": ("会议", "ACM 会议", 2025, "OpenAlex: conference-paper / ACM International Conference（具体会议待补）"),
    # —— 期刊（证据：DOI 的 OpenAlex 记录 type=article + 期刊名）——
    "nlgclplus-neighbor-layer-contrastive": ("期刊", "ACM TORS", 2026, "DOI 10.1145/3806231 -> ACM Transactions on Recommender Systems"),
    "maf-kgat-modality-adaptive-fusion": ("期刊", "计算机科学与应用", 2026, "DOI 10.12677/csa.2026.163084 -> Computer Science and Application"),
    "ammrm-noise-filtering-adaptive-fusion": ("期刊", "JKSU-CIS", 2025, "DOI 10.1007/s44443-025-00026-1 -> J. King Saud Univ. Comput. Inf. Sci."),
    "maritime-remote-operation-certification": ("期刊", "Automatisierungstechnik", 2025, "OpenAlex: article / at - Automatisierungstechnik"),
    "pipe-flow-turbulence-transition": ("期刊", "New Journal of Physics", 2025, "OpenAlex: article / New Journal of Physics"),
    "research-paper-recsys-survey": ("期刊", "Applied Sciences", 2025, "OpenAlex: article / Applied Sciences（中等可信，待核）"),
    # —— 其余一律预印本（无任何已发表证据）——
}


def fm_span(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (m.start(1), m.end(1)) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("posts_dir")
    ap.add_argument("--apply", action="store_true", help="真正写入（默认 dry-run）")
    a = ap.parse_args()

    files = sorted(glob.glob(os.path.join(a.posts_dir, "*.md")))
    stat = {"会议": 0, "期刊": 0, "arXiv预印本": 0}
    changed = 0
    rows = []
    for f in files:
        slug = os.path.basename(f)[:-3]
        text = open(f, encoding="utf-8").read()
        sp = fm_span(text)
        if not sp:
            print(f"  ! {slug} 无 front matter，跳过", file=sys.stderr)
            continue
        fm = text[sp[0]:sp[1]]
        if re.search(r"^venue_type:", fm, re.M):
            rows.append((slug, "已存在", "", "", ""))
            continue
        vt, vn, yr, why = RULE.get(slug, ("arXiv预印本", "arXiv", None, "无已发表证据 -> 预印本"))
        if yr is None:
            d = re.search(r"^date:\s*(\d{4})", fm, re.M)
            yr = int(d.group(1)) if d else 2026
        add = f"year: {yr}\nvenue_type: {vt}\nvenue_name: {vn}\n"
        # 插到 date: 行之后
        m = re.search(r"^date:.*$", fm, re.M)
        if m:
            fm2 = fm[:m.end()] + "\n" + add.rstrip("\n") + fm[m.end():]
        else:
            fm2 = add + fm
        stat[vt] += 1
        changed += 1
        rows.append((slug, vt, vn, yr, why))
        if a.apply:
            open(f, "w", encoding="utf-8", newline="\n").write(text[:sp[0]] + fm2 + text[sp[1]:])

    # 对照表：venue_name -> 篇数
    from collections import Counter
    c = Counter(r[2] for r in rows if r[1] in ("会议", "期刊"))
    print(f"\n共 {len(files)} 篇，{'写入' if a.apply else '待写入'} {changed} 篇")
    print(f"  会议 {stat['会议']} / 期刊 {stat['期刊']} / arXiv预印本 {stat['arXiv预印本']}")
    print("\n会议与期刊的 venue 分布：")
    for k, v in sorted(c.items(), key=lambda x: -x[1]):
        print(f"  {k:<26} {v}")
    print("\n逐篇判定（venue_type / venue_name / year / 依据）：")
    for slug, vt, vn, yr, why in rows:
        if vt == "已存在":
            print(f"  - {slug[:44]:<46} 已有 venue_type，跳过")
        else:
            print(f"  · {slug[:44]:<46} {vt:<10} {vn:<22} {yr}  ← {why}")


if __name__ == "__main__":
    main()
