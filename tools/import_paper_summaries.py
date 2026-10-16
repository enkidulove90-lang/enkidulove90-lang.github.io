#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把本地论文速读摘要导入为 Hexo 文章（写入 source/_posts/）。

用法:
    python tools/import_paper_summaries.py <摘要目录> [--dry-run]

安全约束（公开站点，必须守）:
  1. 自动截断内部章节：任何形如「维度 11 …」「与你的方案关系」「对 … 项目的可迁移要点」
     「项目关联」的标题，及其之后的内容一律不发布。
  2. 正文命中内部关键词（PRISM / LightGCNpp / 本课题 / 我们的实验 …）时**拒绝写入该篇**并报错，
     避免把未发表研究的线索带进公开仓库。
  3. 去掉摘要末尾的机器生成署名（`*由 DeepSeek … 自动生成*` 与尾部横线）。
  4. 不改动摘要源文件，只读。
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(ROOT, "source", "_posts")

# 首批 3 类共 10 篇（精选速读版：无 11 维度长版、体量 1–4KB）
MANIFEST = [
    # —— 多模态推荐 ——
    {"file": "2506.00107_RLMultimodalRec：门控多模态图推荐_summary.md", "category": "多模态推荐",
     "tags": ["多模态", "门控融合", "图神经网络"], "slug": "rlmultimodalrec-gated-fusion"},
    {"file": "2601.22498_FITMM：自适应频率感知多模态推荐_summary.md", "category": "多模态推荐",
     "tags": ["多模态", "频域建模", "自适应融合"], "slug": "fitmm-frequency-aware-multimodal"},
    {"file": "2602.20723_MAGNET：模态引导图专家网络_summary.md", "category": "多模态推荐",
     "tags": ["多模态", "专家网络", "图推荐"], "slug": "magnet-modality-guided-experts"},
    {"file": "2512.20916_多模态大模型摘要与检索增强序列推荐_summary.md", "category": "多模态推荐",
     "tags": ["多模态", "大语言模型", "检索增强"], "slug": "multimodal-summary-rag-seqrec"},
    # —— 知识图谱推荐 ——
    {"file": "2605.28175_混合专家知识图谱检索增强推荐_summary.md", "category": "知识图谱推荐",
     "tags": ["知识图谱", "检索增强", "混合专家"], "slug": "mixragrec-moe-kg-retrieval"},
    {"file": "2601.13969_自适应知识图谱检索器_summary.md", "category": "知识图谱推荐",
     "tags": ["知识图谱", "检索增强", "自适应检索"], "slug": "adaptive-kg-retriever"},
    {"file": "2505.20773_冷启动推荐的知识引导检索增强生成_summary.md", "category": "知识图谱推荐",
     "tags": ["知识图谱", "检索增强", "冷启动"], "slug": "kg-guided-rag-cold-start"},
    # —— LLM 与生成式推荐 ——
    # 注意：以下两篇已移出（不是笔误）。它们的 arXiv 编号在摘要库里挂错，
    # 反查 OpenAlex/arXiv 均未找到标题对应的真实论文，疑似摘要系凭空生成：
    #   · 2505.00556 → 实际是数学论文 "WHEN IS A + xA = R"
    #   · 2504.00678 → 实际是 "RapidPD: 人宠 Wi-Fi 检测"
    # 文章已挪到 source/_drafts/，等补到真实原文再恢复，切莫加回本清单。
    {"file": "2502.09058_LLM增强的推荐去噪框架_summary.md", "category": "LLM与生成式推荐",
     "tags": ["LLM", "去噪", "推荐系统"], "slug": "llm-denoising-recommendation"},
    # —— 大语言模型与Agent ——
    # 以下条目「编号 ↔ 标题」都正确，只是选题本身不属于推荐系统。
    # 按用户决定：不丢弃，另开分类归档，避免污染推荐系统主题的池子。
    {"file": "2605.10730_summary.md", "category": "大语言模型与Agent",
     "tags": ["多模态大模型", "图像生成", "技术报告"], "slug": "qwen-image-2-technical-report",
     "arxiv": "2605.10730", "date": "2026-05-11"},
    {"file": "2608.00267_summary.md", "category": "大语言模型与Agent",
     "tags": ["智能体", "编码智能体", "评测基准"], "slug": "loopsbench-coding-agent-eval",
     "arxiv": "2608.00267", "date": "2026-07-31", "updated": "2026-08-10"},
    {"file": "2606.12373_summary.md", "category": "大语言模型与Agent",
     "tags": ["智能体", "推理泛化", "可验证环境"], "slug": "verifiable-environments-lego-bricks",
     "arxiv": "2606.12373", "date": "2026-06-10"},
    {"file": "2607.02980_summary.md", "category": "大语言模型与Agent",
     "tags": ["大语言模型", "稀疏注意力", "长上下文"], "slug": "hierarchical-sparse-attention",
     "arxiv": "2607.02980", "date": "2026-07-03"},
    {"file": "2606.24597_summary.md", "category": "大语言模型与Agent",
     "tags": ["智能体", "世界模型", "大语言模型"], "slug": "qwen-agentworld",
     "arxiv": "2606.24597", "date": "2026-06-23"},
    # 2507.02097：v1 标题「Agentic Recommender Systems: Architectures, Challenges, and
    # Evaluation」、v3 改为「The Future is Agentic: … Multi-Agent Recommender Systems」，
    # 是同一篇论文（arXiv 版本号重命名），故属于真实可发布内容
    {"file": "2507.02097_多智能体推荐系统的未来_summary.md", "category": "大语言模型与Agent",
     "tags": ["智能体推荐", "多智能体", "综述"], "slug": "future-agentic-multi-agent-recsys",
     "arxiv": "2507.02097", "date": "2025-07-02", "updated": "2026-06-28"},
    # —— 其他领域 ——
    # 编号正确、但与推荐系统及 LLM/Agent 都无关（湍流物理、海事认证），
    # 单独归档，便于日后一并迁移或清理
    {"file": "2503.00987_summary.md", "category": "其他领域",
     "tags": ["流体力学", "随机模型", "湍流"], "slug": "pipe-flow-turbulence-transition",
     "arxiv": "2503.00987", "date": "2025-03-02"},
    {"file": "2508.00543_summary.md", "category": "其他领域",
     "tags": ["海事", "安全认证", "远程操作"], "slug": "maritime-remote-operation-certification",
     "arxiv": "2508.00543", "date": "2025-08-01", "updated": "2025-11-14"},
]

# 命中即截断的章节标题（内部内容，不公开）
STOP_SECTION = re.compile(
    r"^#{2,3}\s*(维度\s*11|与你的方案关系|对.{0,12}项目的可迁移要点|项目关联)"
)
# 命中即拒绝发布的关键词（未发表研究线索）
LEAK_WORDS = ["PRISM", "LightGCNpp", "LightGCN++", "本课题", "我们的实验", "我们的方法",
              "MMEACR", "E14", "E15", "MIG", "syn 专家"]
# 末尾机器署名（变体很多：*由 DeepSeek (deepseek-chat) 自动生成 | 11 维度模板*、
# *由 Claude 生成*、*由 Claude 基于论文全文 + 多源交叉验证生成* …）
# 只匹配「整行以 *由 / 由 开头」的短行，避免误伤正文里"由 LLM 生成推荐"这类正常表述
MACHINE_NOTE = re.compile(
    r"^\*?\s*由\s*(?:DeepSeek|GPT|ChatGPT|Claude|Gemini|Qwen|Kimi|文心|通义|AI)\b[^\n]{0,80}$",
    re.M | re.I,
)


def strip_machine_note(text):
    """去掉末尾的机器生成署名与收尾横线。"""
    text = MACHINE_NOTE.sub("", text)
    return re.sub(r"\n+(?:-{3,}\s*\n*)+\s*$", "\n", text).rstrip()


# 旧的一级分类名 → 新的「领域大类 / 二级分类」路径（三维分类，2026-10-16 改版）
LOG1_CATEGORIES = {
    "多模态推荐": ["推荐系统", "多模态推荐"],
    "知识图谱推荐": ["推荐系统", "知识图谱"],
    "LLM与生成式推荐": ["推荐系统", "生成式推荐"],
    "大语言模型与Agent": ["AI", "大模型与智能体"],
    "其他领域": ["跨学科与基础"],
}

# 摘要头部的机器元信息行（生成时间 / GitHub 待查 等对读者无意义）
META_LINE = re.compile(
    r"^\*\*(英文标题|中文标题|论文标题|作者|会议|期刊|venue|年份|论文类型|一句话概括|"
    r"创新评估|创新评级|GitHub|代码|DOI|来源|源文件|摘要总字符数|实际解析论文数|"
    r"生成时间|生成模型)\*\*[:：].*$",
    re.M | re.I,
)
ARXIV_LINE = re.compile(r"^\*\*arXiv\s*ID\*\*[:：]\s*(\S+)\s*$", re.M)


# 长版摘要（11 维度模板）的标题：「## 维度 3: 主要创新点」→「## 主要创新点」
DIM_ANY = re.compile(r"^(#{2,3})\s*维度\s*\d+\s*[:：]\s*", re.M)
# 「## 维度 0: 元信息」是机器元信息 + 字段表，整节（含正文）丢弃。
# 按行扫描而不是一次性正则，避免 CRLF / 残留分隔线导致的漏删
DIM_META_HEAD = re.compile(r"^#{2,3}\s*维度\s*0\s*[:：]\s*元信息")
ANY_HEAD = re.compile(r"^#{2,3}\s")


def strip_dim_headings(text):
    out, skip = [], False
    for ln in text.splitlines():
        if DIM_META_HEAD.match(ln):
            skip = True
            continue
        if skip:
            if ANY_HEAD.match(ln):   # 遇到下一个章节标题才恢复
                skip = False
            else:
                continue
        out.append(ln)
    text = DIM_ANY.sub(r"\1 ", "\n".join(out))
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def clean_meta(text, emit_arxiv=True):
    """把机器元信息块整理成一行干净的 arXiv 出处。"""
    m = ARXIV_LINE.search(text)
    arxiv = m.group(1) if m else ""
    text = ARXIV_LINE.sub("", text)
    text = META_LINE.sub("", text)
    text = strip_dim_headings(text)   # 丢掉「维度 0: 元信息」整节，并规整「维度 N:」标题
    text = re.sub(r"^[ \t]+$", "", text, flags=re.M)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    text = re.sub(r"^(?:-{3,}[ \t]*\n+)+", "", text)  # 去掉残留的首部横线
    if emit_arxiv and arxiv and arxiv.lower() not in ("待查", "无", "n/a"):
        text = f"> arXiv: {arxiv}\n\n" + text
    return text.strip()


def strip_internal(text):
    """截断第一个内部章节及其后全部内容，返回 (正文, 被截掉的首个标题)。"""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if STOP_SECTION.match(ln):
            return "\n".join(lines[:i]).rstrip(), ln.strip()
    return text.rstrip(), None


def take_title(text):
    """取首个一级标题作为文章标题，并从正文里去掉它。"""
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("# "):
            return ln[2:].strip(), "\n".join(lines[:i] + lines[i + 1:]).lstrip()
    return None, text


def take_summary(text, limit=90):
    """从「主要贡献」小节抽一句话做列表摘要。"""
    m = re.search(r"^#{2,3}\s*(?:主要贡献|创新点)\s*$", text, re.M)
    if not m:
        return ""
    rest = text[m.end():].lstrip("\n")
    for ln in rest.splitlines():
        s = ln.strip()
        if s and not s.startswith("#"):
            s = re.sub(r"^[-*\d.\s]+", "", s)
            return s[:limit] + ("…" if len(s) > limit else "")
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("summaries_dir", help="论文摘要目录（data/summaries）")
    ap.add_argument("--dry-run", action="store_true", help="只报告，不写文件")
    ap.add_argument("--force", action="store_true",
                    help="覆盖已存在的文章（默认跳过，避免冲掉手工精修过的版本）")
    args = ap.parse_args()

    if not os.path.isdir(args.summaries_dir):
        sys.exit(f"目录不存在: {args.summaries_dir}")
    os.makedirs(POSTS, exist_ok=True)

    ok, rejected, skipped = 0, [], []
    for idx, item in enumerate(MANIFEST):
        src = os.path.join(args.summaries_dir, item["file"])
        if not os.path.exists(src):
            rejected.append((item["file"], "源文件不存在"))
            continue
        with open(src, encoding="utf-8") as f:
            raw = f.read()

        title, body = take_title(raw)
        if not title:
            rejected.append((item["file"], "未找到标题"))
            continue

        body, cut = strip_internal(body)
        body = clean_meta(strip_machine_note(body), emit_arxiv=not item.get("arxiv"))

        leaks = sorted({w for w in LEAK_WORDS if w in body})
        if leaks:
            rejected.append((item["file"], "命中内部关键词: " + ", ".join(leaks)))
            continue

        desc = take_summary(body)
        # 优先用论文的真实发布日期；未提供时按 12:40 起每篇错开 1 分钟（保证排序稳定）
        date = item.get("date") or f"2026-10-16 12:{40 + idx:02d}:00"
        fm = [
            "---",
            "title: " + json.dumps(title, ensure_ascii=False),
            "date: " + date,
        ]
        if item.get("updated"):
            fm.append("updated: " + item["updated"])
        fm += [
            "categories: [" + ", ".join(LOG1_CATEGORIES.get(item["category"], [item["category"]])
                                        if isinstance(item["category"], str) else item["category"]) + "]",
            "tags: [" + ", ".join(["论文速读"] + item["tags"]) + "]",
            "slug: " + item["slug"],
            # 封面不写死：交给主题的 cover.default_cover 池在每次构建时随机分配
            # （池内是固定 seed 图，fastly 有 30 天 immutable 缓存，故不影响加载速度；
            #  若要给某篇钉死封面，在这里补一行 cover: <url> 即可）
        ]
        if desc:
            fm.append("description: " + json.dumps(desc, ensure_ascii=False))
        fm.append("---")
        # 论文 / 代码出处行（每篇都附）
        links = []
        if item.get("arxiv"):
            links.append(f"论文：[arXiv {item['arxiv']}](https://arxiv.org/abs/{item['arxiv']})")
        if item.get("github"):
            links.append(f"代码：[GitHub]({item['github']})")
        head = "> " + " · ".join(links) + "\n\n" if links else ""
        post = "\n".join(fm) + "\n\n" + head + body + "\n"

        out = os.path.join(POSTS, item["slug"] + ".md")
        if os.path.exists(out) and not args.force:
            skipped.append((item["slug"], "文章已存在（可能手工精修过），需 --force 才覆盖"))
            continue
        if not args.dry_run:
            with open(out, "w", encoding="utf-8", newline="\n") as f:
                f.write(post)
        ok += 1
        extra = f"  [已截断内部章节: {cut}]" if cut else ""
        print(f"  + {title}  ->  {item['slug']}.md  ({len(post)}B){extra}")

    print(f"\n写入 {ok} 篇，跳过 {len(skipped)} 篇，拒绝 {len(rejected)} 篇")
    for name, why in skipped:
        print(f"  - 跳过 {name}: {why}")
    for name, why in rejected:
        print(f"  ! {name}: {why}", file=sys.stderr)
    return 1 if rejected else 0


if __name__ == "__main__":
    sys.exit(main())
