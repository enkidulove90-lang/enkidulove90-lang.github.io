#!/usr/bin/env python3
"""Download arXiv source archives and extract author-provided figure assets."""

from __future__ import annotations

import argparse
import gzip
import json
import re
import shutil
import subprocess
import tarfile
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import fitz
from PIL import Image


FIGURE = re.compile(
    r"\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}", re.I | re.S
)
INCLUDE = re.compile(
    r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", re.I
)
GRAPHICSPATH = re.compile(r"\\graphicspath\{((?:\{[^}]+\})+)\}", re.I | re.S)
BRACED_PATH = re.compile(r"\{([^}]+)\}")
EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".pdf", ".eps", ".svg")


@dataclass(frozen=True)
class SourceFigure:
    path: Path
    caption: str
    dimensions: tuple[int, int]
    is_hd: bool
    provenance: str = "arxiv_source"


METHOD_TERMS = re.compile(
    r"architecture|framework|overview|pipeline|paradigm|proposed|system|training|method",
    re.I,
)
RESULT_TERMS = re.compile(
    r"ablation|benchmark|performance|comparison|evaluation|result|impact|distribution",
    re.I,
)


def select_source_figures(assets: list[SourceFigure], limit: int = 3) -> list[SourceFigure]:
    """Keep a compact, source-ordered set covering method and result evidence."""
    eligible = [asset for asset in assets if asset.is_hd and asset.caption]
    chosen: list[SourceFigure] = []
    for pattern in (METHOD_TERMS, RESULT_TERMS):
        match = next(
            (asset for asset in eligible if asset not in chosen and pattern.search(asset.caption)),
            None,
        )
        if match:
            chosen.append(match)
    for asset in eligible:
        if len(chosen) >= limit:
            break
        if asset not in chosen:
            chosen.append(asset)
    positions = {id(asset): index for index, asset in enumerate(eligible)}
    return sorted(chosen[:limit], key=lambda asset: positions[id(asset)])


def _is_hd(dimensions: tuple[int, int]) -> bool:
    return dimensions[0] >= 1280 or dimensions[1] >= 720


def _clean_latex(text: str) -> str:
    text = re.sub(r"(?<!\\)%.*", "", text)
    text = re.sub(r"\\(?:textbf|textit|emph|mathrm|texttt)\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\(?:label|ref|cite)\{[^{}]*\}", "", text)
    text = text.replace("~", " ")
    text = text.replace(r"\%", "%")
    return re.sub(r"\s+", " ", text).strip()


def _balanced_argument(text: str, command: str) -> str:
    match = re.search(rf"\\{command}(?:\[[^]]*\])?\s*\{{", text, re.I)
    if not match:
        return ""
    start = match.end() - 1
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{" and (index == 0 or text[index - 1] != "\\"):
            depth += 1
        elif text[index] == "}" and (index == 0 or text[index - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return text[start + 1 : index]
    return ""


def _resolve_graphic(source_root: Path, tex_path: Path, name: str, paths: list[str]) -> Path | None:
    raw = name.strip().replace("\\", "/")
    candidates: list[Path] = []
    bases = [tex_path.parent, source_root]
    bases.extend(tex_path.parent / item for item in paths)
    for base in bases:
        candidate = base / raw
        if candidate.suffix:
            candidates.append(candidate)
        else:
            candidates.extend(candidate.with_suffix(ext) for ext in EXTENSIONS)
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def _render_asset(source: Path, destination: Path) -> tuple[int, int] | None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    suffix = source.suffix.lower()
    try:
        if suffix == ".pdf":
            document = fitz.open(source)
            try:
                if not len(document):
                    return None
                document[0].get_pixmap(dpi=300, alpha=False).save(destination)
            finally:
                document.close()
        elif suffix == ".svg":
            document = fitz.open(stream=source.read_bytes(), filetype="svg")
            try:
                document[0].get_pixmap(dpi=300, alpha=False).save(destination)
            finally:
                document.close()
        else:
            with Image.open(source) as image:
                if "A" in image.getbands() or "transparency" in image.info:
                    rgba = image.convert("RGBA")
                    rendered = Image.new("RGB", rgba.size, "white")
                    rendered.paste(rgba, mask=rgba.getchannel("A"))
                else:
                    rendered = image.convert("RGB")
                rendered.save(destination, format="PNG")
        with Image.open(destination) as rendered:
            return rendered.size
    except (OSError, RuntimeError, ValueError):
        return None


def extract_source_figures(source_root: Path, output_dir: Path) -> list[SourceFigure]:
    source_root = Path(source_root).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    assets: list[SourceFigure] = []
    seen: set[tuple[Path, str]] = set()
    tex_files = sorted(source_root.rglob("*.tex"))
    all_text = [path.read_text(encoding="utf-8", errors="replace") for path in tex_files]
    global_graphic_paths = [
        item.strip().replace("\\", "/")
        for text in all_text
        for match in GRAPHICSPATH.finditer(text)
        for item in BRACED_PATH.findall(match.group(1))
    ]
    for tex_path, text in zip(tex_files, all_text):
        graphic_paths = [
            item.strip().replace("\\", "/")
            for match in GRAPHICSPATH.finditer(text)
            for item in BRACED_PATH.findall(match.group(1))
        ]
        graphic_paths = list(dict.fromkeys(graphic_paths + global_graphic_paths))
        for figure in FIGURE.finditer(text):
            body = figure.group(1)
            caption = _clean_latex(_balanced_argument(body, "caption"))
            if not caption:
                continue
            for include in INCLUDE.finditer(body):
                source = _resolve_graphic(source_root, tex_path, include.group(1), graphic_paths)
                if not source or (source, caption) in seen:
                    continue
                seen.add((source, caption))
                destination = output_dir / f"figure_{len(assets) + 1:03d}_{source.stem}.png"
                dimensions = _render_asset(source, destination)
                if not dimensions:
                    continue
                assets.append(
                    SourceFigure(
                        path=destination,
                        caption=caption,
                        dimensions=dimensions,
                        is_hd=_is_hd(dimensions),
                    )
                )
    return assets


def unpack_source_archive(archive: Path, destination: Path) -> Path:
    archive = Path(archive)
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    try:
        with tarfile.open(archive, mode="r:*") as bundle:
            root = destination.resolve()
            for member in bundle.getmembers():
                if not member.isfile() or member.issym() or member.islnk():
                    continue
                target = (destination / member.name).resolve()
                if root not in target.parents and target != root:
                    raise ValueError(f"unsafe arXiv source path: {member.name}")
                target.parent.mkdir(parents=True, exist_ok=True)
                source = bundle.extractfile(member)
                if source:
                    with source, target.open("wb") as output:
                        shutil.copyfileobj(source, output)
            return destination
    except tarfile.ReadError:
        raw = archive.read_bytes()
        try:
            raw = gzip.decompress(raw)
        except (gzip.BadGzipFile, OSError):
            pass
        if b"\\documentclass" not in raw and b"\\begin{document}" not in raw:
            raise ValueError(f"unsupported arXiv source archive: {archive}")
        (destination / "main.tex").write_bytes(raw)
        return destination


def fetch_and_extract(arxiv_id: str, output_root: Path) -> dict:
    paper_root = Path(output_root) / arxiv_id / "arxiv-source"
    archive = paper_root / "source.tar"
    unpacked = paper_root / "unpacked"
    figures = paper_root / "figures"
    paper_root.mkdir(parents=True, exist_ok=True)
    if not archive.exists():
        partial = paper_root / "source.tar.part"
        subprocess.run(
            [
                "curl.exe",
                "-L",
                "--fail",
                "--silent",
                "--show-error",
                "--retry",
                "1",
                "--retry-delay",
                "5",
                "-A",
                "paper-source-extractor/1.0",
                f"https://export.arxiv.org/e-print/{arxiv_id}",
                "-o",
                str(partial),
            ],
            check=True,
        )
        if partial.stat().st_size < 1024:
            raise ValueError(f"arXiv source archive is too small: {arxiv_id}")
        partial.replace(archive)
    source_format = "source"
    if archive.read_bytes()[:5] == b"%PDF-":
        source_format = "pdf_only"
        assets = []
    else:
        if not unpacked.exists():
            unpack_source_archive(archive, unpacked)
        assets = extract_source_figures(unpacked, figures)
    return {
        "arxiv_id": arxiv_id,
        "archive": str(archive.resolve()),
        "archive_bytes": archive.stat().st_size,
        "source_format": source_format,
        "figure_count": len(assets),
        "hd_figure_count": sum(asset.is_hd for asset in assets),
        "figures": [
            {**asdict(asset), "path": str(asset.path), "dimensions": list(asset.dimensions)}
            for asset in assets
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", required=True, help="Comma-separated arXiv IDs")
    parser.add_argument("--output-root", type=Path, default=Path(".paper-work"))
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    results = []
    for index, arxiv_id in enumerate(item.strip() for item in args.ids.split(",") if item.strip()):
        if index:
            time.sleep(1)
        try:
            results.append(fetch_and_extract(arxiv_id, args.output_root))
        except (subprocess.CalledProcessError, OSError, ValueError) as error:
            results.append({"arxiv_id": arxiv_id, "error": str(error)})
    report = {"schema_version": 1, "items": results}
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
    print(text, end="")
    return 1 if any("error" in item for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
