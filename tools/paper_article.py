#!/usr/bin/env python3
"""Render evidence-backed paper articles and enforce publication gates."""

from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from mineru_adapter import FigureAsset, ParsedPaper


REQUIRED_SECTIONS = (
    "## 一、简介",
    "## 二、论文方法",
    "## 三、论文里的图与解释",
    "## 四、模块创新点",
    "## 五、实验数据集选择",
    "## 六、消融实验",
    "## 七、Benchmark 结果与解释",
    "## 八、总结",
    "## References",
)
LEAK_MARKERS = ("本课题", "我们的实验", "我们的方法", "MMEACR", "E14", "E15", "MIG", "syn 专家")
PERCENTAGE = re.compile(r"(?<![\d.])\d+(?:\.\d+)?%")
GITHUB = re.compile(r"https?://github\.com/[\w.-]+/[\w.-]+", re.I)
HEADING = re.compile(r"(?m)^#{1,3}\s+(.+?)\s*$")


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
    for name, content in sections.items():
        if any(re.search(pattern, name, re.I) for pattern in patterns) and content.strip():
            return content.strip(), name
    return fallback, "explicit absence"


def _frontmatter(title: str, paper_id: str) -> str:
    year = 2000 + int(paper_id[:2])
    month = int(paper_id[2:4])
    safe_title = title.replace('"', "'")
    return (
        "---\n"
        f'title: "{safe_title}"\n'
        f"date: {year:04d}-{month:02d}-01\n"
        f"year: {year}\n"
        'venue_type: "arXiv预印本"\n'
        'venue_name: "arXiv"\n'
        "categories: [推荐系统, 论文速递]\n"
        "tags: [论文速递]\n"
        f"slug: paper-{paper_id}\n"
        f'arxiv_id: "{paper_id}"\n'
        "---"
    )


def build_article(
    record,
    parsed: ParsedPaper,
    summary_path: Path | None,
    include_source_pdf: bool = True,
) -> ArticleDraft:
    summary_text, summary_sections = _summary_sections(Path(summary_path) if summary_path else None)
    combined_sections = dict(parsed.sections)
    combined_sections.update(summary_sections)
    title = record.summary_title or record.parsed_title or next(
        (name for name in parsed.sections if name.lower() not in {"abstract", "references"}),
        f"论文 {record.arxiv_id}",
    )

    intro, intro_source = _pick(
        combined_sections,
        (r"主要贡献|简介|摘要|abstract",),
        "论文解析稿未提供可可靠复述的摘要。",
    )
    method, method_source = _pick(
        combined_sections,
        (r"方法|method|approach|framework",),
        "论文未报告可独立提取的方法章节。",
    )
    innovation, innovation_source = _pick(
        combined_sections,
        (r"创新|contribution",),
        "论文未单列模块创新点；请以方法章节和原文贡献陈述为准。",
    )
    dataset, dataset_source = _pick(
        combined_sections,
        (r"数据集|实验设置|dataset|experimental setup",),
        "论文未报告可独立提取的数据集选择说明。",
    )
    ablation, ablation_source = _pick(
        combined_sections,
        (r"消融|ablation",),
        "论文未报告独立的消融实验。",
    )
    benchmark, benchmark_source = _pick(
        combined_sections,
        (r"实验结果|benchmark|result|performance",),
        "论文未报告可独立提取的 benchmark 结果。",
    )
    conclusion, conclusion_source = _pick(
        combined_sections,
        (r"总结|结论|conclusion",),
        "论文未提供可独立提取的总结章节。",
    )
    references, references_source = _pick(
        parsed.sections,
        (r"references|参考文献",),
        "完整参考文献请见论文原文。",
    )
    references = references[:4000]

    hd_figures = [figure for figure in parsed.figures if figure.is_hd]
    figure_lines: list[str] = []
    for index, figure in enumerate(hd_figures, 1):
        public_path = f"/images/papers/{record.arxiv_id}/{figure.path.name}"
        caption = figure.caption or f"Figure {index}（原解析稿未保留图注）"
        figure_lines.extend(
            [
                f"### 图 {index}",
                f"![{caption}]({public_path})",
                f"**原图说明：** {caption}",
                f"**图示解释：** 该图对应论文中的“{caption}”。图中细节应结合相邻方法与实验文字阅读，不对原文未说明的关系作额外推断。",
            ]
        )
    if not figure_lines:
        figure_lines.append("论文解析资产中未找到满足高清门槛且可与图注可靠对应的原图。")

    github_links = sorted(set(GITHUB.findall(parsed.normalized_markdown + "\n" + summary_text)))
    reference_links = [f"- [论文：arXiv {record.arxiv_id}](https://arxiv.org/abs/{record.arxiv_id})"]
    reference_links.extend(f"- [代码：GitHub]({link.rstrip('.,')})" for link in github_links)
    source_pdf = Path(record.pdf_path).resolve() if include_source_pdf and Path(record.pdf_path).exists() else None
    if source_pdf:
        reference_links.append(f"- [PDF源文件](/papers/{record.arxiv_id}.pdf)")
    elif not github_links:
        reference_links.append("- 论文未提供可验证的官方 GitHub 仓库链接。")

    markdown = "\n\n".join(
        [
            _frontmatter(title, record.arxiv_id),
            "## 一、简介",
            intro,
            "## 二、论文方法",
            method,
            "## 三、论文里的图与解释",
            "\n\n".join(figure_lines),
            "## 四、模块创新点",
            innovation,
            "## 五、实验数据集选择",
            dataset,
            "## 六、消融实验",
            ablation,
            "## 七、Benchmark 结果与解释",
            benchmark,
            "## 八、总结",
            conclusion,
            "## References",
            references,
            "### 在线资源",
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
