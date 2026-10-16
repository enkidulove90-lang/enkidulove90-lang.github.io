#!/usr/bin/env python3
"""Normalize MinerU outputs and retain figure provenance."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

import fitz
from PIL import Image

from arxiv_source_figures import extract_source_figures, select_source_figures


IMAGE_REF = re.compile(r"!\[[^]]*\]\(([^)]+)\)")
CAPTION = re.compile(
    r"(?im)^\s*((?:Figure|Fig\.|Table)\s*(?:\d+(?:\.\d+)?|[A-Z])\s*(?:[:.]\s*)?.+)$"
)
HEADING = re.compile(r"(?m)^(#{1,3})\s+(.+?)\s*$")


class ParseRequired(RuntimeError):
    pass


class MinerUUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class FigureAsset:
    path: Path
    caption: str
    dimensions: tuple[int, int]
    is_hd: bool
    provenance: str
    page_number: int | None = None


@dataclass(frozen=True)
class ParsedPaper:
    arxiv_id: str
    markdown_path: Path
    normalized_markdown: str
    sections: dict[str, str]
    figures: list[FigureAsset] = field(default_factory=list)


def is_hd_image(width: int, height: int) -> bool:
    return width >= 1280 or height >= 720


def _normalize_markdown(text: str) -> str:
    text = re.sub(r"</?su[bp]>", "", text)
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _sections(text: str) -> dict[str, str]:
    headings = list(HEADING.finditer(text))
    sections: dict[str, str] = {}
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        sections[heading.group(2).strip()] = text[heading.end() : end].strip()
    return sections


def _dimensions(path: Path) -> tuple[int, int]:
    with Image.open(path) as image:
        return image.size


def _caption_after(text: str, end: int) -> str:
    match = CAPTION.search(text[end : end + 1200])
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""


def _block_text(block: dict) -> str:
    return "".join(
        span.get("content", "")
        for line in block.get("lines", [])
        for span in line.get("spans", [])
    ).strip()


def _crop_layout_figures(layout_path: Path, pdf_path: Path, out_dir: Path) -> list[FigureAsset]:
    data = json.loads(layout_path.read_text(encoding="utf-8"))
    doc = fitz.open(pdf_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    figures: list[FigureAsset] = []
    try:
        for page_info in data.get("pdf_info", []):
            page_index = int(page_info.get("page_idx", 0))
            if page_index >= len(doc):
                continue
            blocks = page_info.get("para_blocks") or []
            captions = [block for block in blocks if block.get("type") in {"image_caption", "caption"}]
            for block in blocks:
                if block.get("type") != "image" or not block.get("bbox"):
                    continue
                bbox = fitz.Rect(*block["bbox"]) & doc[page_index].rect
                if bbox.width < 100 or bbox.height < 60:
                    continue
                caption = ""
                if captions:
                    nearest = min(
                        captions,
                        key=lambda item: abs(float((item.get("bbox") or [0, 0])[1]) - bbox.y1),
                    )
                    caption = _block_text(nearest)
                path = out_dir / f"p{page_index + 1}_{int(bbox.x0)}_{int(bbox.y0)}.png"
                doc[page_index].get_pixmap(clip=bbox, dpi=200).save(path)
                dimensions = _dimensions(path)
                figures.append(
                    FigureAsset(
                        path=path.resolve(),
                        caption=caption,
                        dimensions=dimensions,
                        is_hd=is_hd_image(*dimensions),
                        provenance="layout_crop",
                        page_number=page_index + 1,
                    )
                )
    finally:
        doc.close()
    return figures


def _crop_pdf_caption_figures(
    pdf_path: Path, out_dir: Path, *, max_figures: int = 3
) -> list[FigureAsset]:
    """Render source-PDF regions immediately above detected figure captions."""
    doc = fitz.open(pdf_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    figures: list[FigureAsset] = []
    try:
        for page_index, page in enumerate(doc):
            for block in page.get_text("blocks"):
                caption_match = CAPTION.search(str(block[4]).strip())
                if not caption_match:
                    continue
                caption = re.sub(r"\s+", " ", caption_match.group(1)).strip()
                caption_box = fitz.Rect(block[:4])
                top = max(36.0, caption_box.y0 - min(360.0, page.rect.height * 0.48))
                crop = fitz.Rect(36.0, top, page.rect.width - 36.0, caption_box.y0 - 3.0)
                if crop.width < 100 or crop.height < 60:
                    continue
                path = out_dir / f"p{page_index + 1}_caption_{len(figures) + 1}.png"
                page.get_pixmap(clip=crop, dpi=300, alpha=False).save(path)
                dimensions = _dimensions(path)
                figures.append(
                    FigureAsset(
                        path=path.resolve(),
                        caption=caption,
                        dimensions=dimensions,
                        is_hd=is_hd_image(*dimensions),
                        provenance="pdf_caption_crop",
                        page_number=page_index + 1,
                    )
                )
                if len(figures) >= max_figures:
                    return figures
    finally:
        doc.close()
    return figures


def _run_mineru(command: str, pdf_path: Path, output_dir: Path) -> Path:
    executable = shutil.which(command)
    if not executable:
        raise MinerUUnavailable(f"MinerU command not found: {command}")
    output_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run([executable, "-p", str(pdf_path), "-o", str(output_dir)], check=True)
    markdown = sorted(output_dir.rglob("*.md"), key=lambda path: (-path.stat().st_size, str(path)))
    if not markdown:
        raise ParseRequired(f"MinerU produced no Markdown for {pdf_path}")
    return markdown[0]


def prepare_assets(record, output_root: Path, run_mineru: bool, command: str = "mineru") -> ParsedPaper:
    markdown_path = Path(record.parsed_md_path).resolve() if record.parsed_md_path else None
    output_root = Path(output_root)
    if not markdown_path or not markdown_path.exists():
        if not run_mineru:
            raise ParseRequired(f"{record.arxiv_id} has no parsed Markdown")
        markdown_path = _run_mineru(
            command,
            Path(record.pdf_path).resolve(),
            output_root / record.arxiv_id / "mineru",
        )

    text = _normalize_markdown(markdown_path.read_text(encoding="utf-8", errors="replace"))
    figures: list[FigureAsset] = []
    missing_refs: list[tuple[str, str]] = []
    for match in IMAGE_REF.finditer(text):
        relative = match.group(1).replace("/", str(Path("/").anchor or "/"))
        image_path = (markdown_path.parent / Path(relative)).resolve()
        caption = _caption_after(text, match.end())
        if image_path.exists():
            dimensions = _dimensions(image_path)
            figures.append(
                FigureAsset(
                    path=image_path,
                    caption=caption,
                    dimensions=dimensions,
                    is_hd=is_hd_image(*dimensions),
                    provenance="mineru_image",
                )
            )
        else:
            missing_refs.append((match.group(1), caption))

    layouts = sorted(markdown_path.parent.glob("*layout*.json"))
    pdf_path = Path(record.pdf_path).resolve()
    if pdf_path.exists() and not any(item.is_hd for item in figures):
        source_root = output_root / record.arxiv_id / "arxiv-source" / "unpacked"
        if source_root.exists():
            source_figures = select_source_figures(
                extract_source_figures(
                    source_root,
                    output_root / record.arxiv_id / "arxiv-source" / "figures",
                )
            )
            figures.extend(
                FigureAsset(
                    path=item.path,
                    caption=item.caption,
                    dimensions=item.dimensions,
                    is_hd=item.is_hd,
                    provenance=item.provenance,
                )
                for item in source_figures
                if item.is_hd
            )
    layout_crops: list[FigureAsset] = []
    if layouts and pdf_path.exists() and not any(item.is_hd for item in figures):
        layout_crops = _crop_layout_figures(
            layouts[0], pdf_path, output_root / record.arxiv_id / "figures"
        )
        if not any(item.is_hd for item in figures):
            figures.extend(crop for crop in layout_crops if crop.is_hd)

    if missing_refs and layout_crops:
            used: set[Path] = set()
            for _, expected_caption in missing_refs:
                number = re.search(r"(?:Figure|Fig\.|Table)\s*(\d+)", expected_caption, re.I)
                candidates = [crop for crop in layout_crops if crop.path not in used]
                if number:
                    matching = [crop for crop in candidates if re.search(
                        rf"(?:Figure|Fig\.|Table)\s*{number.group(1)}\b", crop.caption, re.I
                    )]
                    candidates = matching or candidates
                if candidates:
                    crop = candidates[0]
                    used.add(crop.path)
                    if crop.path not in {item.path for item in figures}:
                        figures.append(crop)

    if pdf_path.exists() and not any(item.is_hd for item in figures):
        figures.extend(
            _crop_pdf_caption_figures(
                pdf_path, output_root / record.arxiv_id / "pdf-caption-figures"
            )
        )

    return ParsedPaper(
        arxiv_id=record.arxiv_id,
        markdown_path=markdown_path,
        normalized_markdown=text,
        sections=_sections(text),
        figures=figures,
    )
