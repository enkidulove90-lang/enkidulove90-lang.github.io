#!/usr/bin/env python3
"""Render evidence-backed paper articles and enforce publication gates."""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from mineru_adapter import FigureAsset, ParsedPaper


REQUIRED_SECTIONS = (
    "## 研究问题",
    "## 方法：核心思路与整体框架",
    "## 创新点",
    "## 实验：数据、基线与结果",
    "### 数据集与设置",
    "### Benchmark 与结果",
    "### 消融实验",
    "## 总结",
    "## References",
)
LEAK_MARKERS = ("本课题", "我们的实验", "我们的方法", "MMEACR", "E14", "E15", "MIG", "syn 专家")
PERCENTAGE = re.compile(r"(?<![\d.])\d+(?:\.\d+)?%")
GITHUB = re.compile(r"https?://github\.com/[\w.-]+/[\w.-]+", re.I)
HEADING = re.compile(r"(?m)^#{2,3}\s+(.+?)\s*$")


@dataclass(frozen=True)
class ArticleDraft:
    arxiv_id: str
    title: str
    slug: str
    markdown: str
    source_text: str
    figures: list[FigureAsset] = field(default_factory=list)
    source_pdf: Path | None = None
    source_spans: dict[str, str] = field(default_factory=dict)


def _summary_sections(path: Path | None) -> tuple[str, dict[str, str]]:
    if not path or not path.exists():
        return "", {}
    text = path.read_text(encoding="utf-8", errors="replace")
    headings = list(HEADING.finditer(text))
    sections: dict[str, str] = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        sections[heading.group(1).strip()] = text[heading.end() : end].strip()
    return text, sections


def _pick(sections: dict[str, str], patterns: tuple[str, ...], fallback: str) -> tuple[str, str]:
    for pattern in patterns:
        for name, content in sections.items():
            if re.search(pattern, name, re.I) and content.strip():
                return content.strip(), name
    return fallback, "explicit absence"


def _pick_preferred(
    summary_sections: dict[str, str],
    parsed_sections: dict[str, str],
    patterns: tuple[str, ...],
    fallback: str,
) -> tuple[str, str]:
    content, source = _pick(summary_sections, patterns, "")
    if content:
        return content, f"summary:{source}"
    content, source = _pick(parsed_sections, patterns, fallback)
    return content, f"parsed:{source}" if source != "explicit absence" else source


def _summary_display_title(path: Path | None, fallback: str) -> str:
    if not path or not path.exists():
        return fallback
    match = re.search(r"(?m)^#\s+(.+?)\s*$", path.read_text(encoding="utf-8", errors="replace"))
    return match.group(1).strip() if match else fallback


def _first_sentence(text: str, limit: int = 180) -> str:
    clean = re.sub(r"(?m)^[-*]\s+", "", text).replace("**", "")
    clean = re.sub(r"\s+", " ", clean).strip()
    if not clean:
        return ""
    match = re.search(r".+?[。！？]", clean)
    sentence = match.group(0) if match else clean
    return sentence[:limit].rstrip("，,；;：: ") + ("…" if len(sentence) > limit else "")


def _labelled_item(text: str, labels: tuple[str, ...]) -> str:
    for label in labels:
        match = re.search(
            rf"(?ms)^[-*]\s*\*\*{re.escape(label)}\*\*[：:]\s*(.+?)(?=\n[-*]\s*\*\*|\Z)",
            text,
        )
        if match:
            return match.group(1).strip()
    return ""


def _clean_dataset_description(text: str) -> str:
    """Keep structured dataset facts while dropping raw English section dumps."""
    if "；任务：" not in text:
        return text
    dataset, tail = text.split("；任务：", 1)
    split = re.search(r"；(划分|协议|评估协议)：", tail)
    if split:
        return f"{dataset}；{tail[split.start() + 1:]}".strip()
    return dataset.strip()


def _frontmatter(title: str, paper_id: str, description: str) -> str:
    year = 2000 + int(paper_id[:2])
    month = int(paper_id[2:4])
    return (
        "---\n"
        f"title: {json.dumps(title, ensure_ascii=False)}\n"
        f"date: {year:04d}-{month:02d}-01\n"
        f"year: {year}\n"
        'venue_type: "arXiv预印本"\n'
        'venue_name: "arXiv"\n'
        "categories: [推荐系统, 论文速递]\n"
        "tags: [论文速递]\n"
        f"slug: paper-{paper_id}\n"
        f'arxiv_id: "{paper_id}"\n'
        f"description: {json.dumps(description, ensure_ascii=False)}\n"
        "---"
    )


def _figure_block(figure: FigureAsset, paper_id: str, index: int, context: str) -> str:
    public_path = f"/images/papers/{paper_id}/{figure.path.name}"
    caption = figure.caption or f"Figure {index}（原解析稿未保留图注）"
    explanation = _first_sentence(context, 220)
    return "\n\n".join(
        [
            f"![图 {index}：{caption}]({public_path})",
            f"*图 {index} · 原图说明：{caption}*",
            f"**图示解释：** {explanation or '这张图用于补充论文的核心方法或实验结论；具体符号与数值以原文图注为准。'}",
        ]
    )


def _is_result_figure(caption: str) -> bool:
    return bool(
        re.search(
            r"ablation|result|performance|comparison|compare|metric|auc|ndcg|recall|dataset|benchmark|accuracy|latency|throughput|scal|case study|analysis",
            caption,
            re.I,
        )
    )


def build_article(
    record,
    parsed: ParsedPaper,
    summary_path: Path | None,
    include_source_pdf: bool = True,
) -> ArticleDraft:
    summary_text, summary_sections = _summary_sections(Path(summary_path) if summary_path else None)
    english_title = record.summary_title or record.parsed_title or next(
        (name for name in parsed.sections if name.lower() not in {"abstract", "references"}),
        f"论文 {record.arxiv_id}",
    )
    title = _summary_display_title(Path(summary_path) if summary_path else None, english_title)

    intro, intro_source = _pick_preferred(
        summary_sections,
        parsed.sections,
        (r"主要贡献|简介|摘要|abstract",),
        "论文解析稿未提供可可靠复述的摘要。",
    )
    method, method_source = _pick_preferred(
        summary_sections,
        parsed.sections,
        (r"方法|method|approach|framework",),
        "论文未报告可独立提取的方法章节。",
    )
    innovation, innovation_source = _pick_preferred(
        summary_sections,
        parsed.sections,
        (r"创新|contribution",),
        "论文未单列模块创新点；请以方法章节和原文贡献陈述为准。",
    )
    dataset, dataset_source = _pick_preferred(
        summary_sections,
        parsed.sections,
        (r"数据集|实验设置|dataset|experimental setup",),
        "论文未报告可独立提取的数据集选择说明。",
    )
    conditions, conditions_source = _pick_preferred(
        summary_sections,
        parsed.sections,
        (r"实验条件|experimental condition",),
        "",
    )
    condition_dataset = _labelled_item(conditions, ("数据与任务设置", "任务与数据设置"))
    if condition_dataset:
        dataset, dataset_source = _clean_dataset_description(condition_dataset), conditions_source
    ablation, ablation_source = _pick(
        summary_sections,
        (r"消融|ablation",),
        "",
    )
    condition_baselines = _labelled_item(conditions, ("基线与对照", "基线与消融设置"))
    if not ablation and re.search(r"消融|ablation", condition_baselines, re.I):
        ablation, ablation_source = condition_baselines, conditions_source
    if not ablation:
        ablation, ablation_source = "论文未报告独立的消融实验。", "explicit absence"
    benchmark, benchmark_source = _pick_preferred(
        summary_sections,
        parsed.sections,
        (r"实验(?:结果|效果)", r"benchmark", r"result", r"performance"),
        "论文未报告可独立提取的 benchmark 结果。",
    )
    conclusion, conclusion_source = _pick(
        summary_sections,
        (r"总结|结论|conclusion",),
        _first_sentence(intro, 260),
    )
    references_source = "online resources"

    hd_figures = [figure for figure in parsed.figures if figure.is_hd]
    method_figures: list[str] = []
    result_figures: list[str] = []
    for index, figure in enumerate(hd_figures, 1):
        block = _figure_block(
            figure,
            record.arxiv_id,
            index,
            benchmark if _is_result_figure(figure.caption) else method,
        )
        (result_figures if _is_result_figure(figure.caption) else method_figures).append(block)
    if not method_figures and result_figures:
        method_figures.append(result_figures.pop(0))
    if not method_figures:
        method_figures.append("论文解析资产中未找到满足高清门槛且可与图注可靠对应的原图。")

    github_links = sorted(set(GITHUB.findall(parsed.normalized_markdown + "\n" + summary_text)))
    paper_link = f"https://arxiv.org/abs/{record.arxiv_id}"
    resource_parts = [f"论文：[arXiv {record.arxiv_id}]({paper_link})"]
    resource_parts.extend(f"代码：[GitHub]({link.rstrip('.,')})" for link in github_links)
    reference_links: list[str] = []
    reference_links.extend(f"- [代码：GitHub]({link.rstrip('.,')})" for link in github_links)
    source_pdf = Path(record.pdf_path).resolve() if include_source_pdf and Path(record.pdf_path).exists() else None
    if source_pdf:
        resource_parts.append(f"PDF：[本地阅读](/papers/{record.arxiv_id}.pdf)")
        reference_links.append(f"- [PDF源文件](/papers/{record.arxiv_id}.pdf)")
    elif not github_links:
        reference_links.append("- 论文未提供可验证的官方 GitHub 仓库链接。")

    markdown = "\n\n".join(
        [
            _frontmatter(title, record.arxiv_id, _first_sentence(intro)),
            "> " + " · ".join(resource_parts),
            intro,
            "## 研究问题",
            intro,
            "## 方法：核心思路与整体框架",
            method,
            "\n\n".join(method_figures),
            "## 创新点",
            innovation,
            "## 实验：数据、基线与结果",
            "### 数据集与设置",
            dataset,
            "### Benchmark 与结果",
            benchmark,
            "\n\n".join(result_figures),
            "### 消融实验",
            ablation,
            "## 总结",
            conclusion,
            "## References",
            f"- {english_title}：[arXiv {record.arxiv_id}]({paper_link})",
            "\n".join(reference_links),
        ]
    ).strip() + "\n"

    return ArticleDraft(
        arxiv_id=record.arxiv_id,
        title=title,
        slug=f"paper-{record.arxiv_id}",
        markdown=markdown,
        source_text=parsed.normalized_markdown + "\n" + summary_text,
        figures=hd_figures,
        source_pdf=source_pdf,
        source_spans={
            "introduction": intro_source,
            "method": method_source,
            "innovation": innovation_source,
            "dataset": dataset_source,
            "ablation": ablation_source,
            "benchmark": benchmark_source,
            "conclusion": conclusion_source,
            "references": references_source,
        },
    )


def validate_article(draft: ArticleDraft) -> list[str]:
    errors: list[str] = []
    if not draft.figures:
        errors.append("missing article figure")
    for section in REQUIRED_SECTIONS:
        if section not in draft.markdown:
            errors.append(f"missing section: {section}")
    for marker in LEAK_MARKERS:
        if marker in draft.markdown:
            errors.append(f"internal research marker: {marker}")
    source_percentages = set(PERCENTAGE.findall(draft.source_text))
    for value in sorted(set(PERCENTAGE.findall(draft.markdown)) - source_percentages):
        errors.append(f"unsupported numeric claim: {value}")
    if f"https://arxiv.org/abs/{draft.arxiv_id}" not in draft.markdown:
        errors.append("missing arXiv link")
    for figure in draft.figures:
        if not figure.path.exists():
            errors.append(f"missing figure: {figure.path}")
        elif not figure.is_hd:
            errors.append(f"non-HD figure: {figure.path.name}")
        if not figure.caption:
            errors.append(f"missing figure caption: {figure.path.name}")
    if draft.figures and "图示解释：" not in draft.markdown:
        errors.append("missing figure explanation")
    if draft.source_pdf and not draft.source_pdf.exists():
        errors.append(f"missing source PDF: {draft.source_pdf}")
    return errors


def materialize_article(draft: ArticleDraft, site_root: Path) -> Path:
    errors = validate_article(draft)
    if errors:
        raise ValueError("article validation failed: " + "; ".join(errors))
    site_root = Path(site_root)
    image_dir = site_root / "source" / "images" / "papers" / draft.arxiv_id
    image_dir.mkdir(parents=True, exist_ok=True)
    for figure in draft.figures:
        shutil.copy2(figure.path, image_dir / figure.path.name)
    if draft.source_pdf:
        pdf_dir = site_root / "source" / "papers"
        pdf_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(draft.source_pdf, pdf_dir / f"{draft.arxiv_id}.pdf")
    posts = site_root / "source" / "_posts"
    posts.mkdir(parents=True, exist_ok=True)
    output = posts / f"paper-{draft.arxiv_id}.md"
    output.write_text(draft.markdown, encoding="utf-8", newline="\n")
    return output
