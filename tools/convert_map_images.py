"""Convert locally cached map photos to compact WebP and rewrite places.json."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = ROOT / "source" / "images" / "map"
PLACES_PATH = ROOT / "source" / "_data" / "places.json"
SOURCE_SUFFIXES = {".jpg", ".jpeg", ".png"}


def convert(*, remove_originals: bool = False, quality: int = 76, max_width: int = 1280) -> dict:
    replacements: dict[str, str] = {}
    before_bytes = 0
    after_bytes = 0
    converted = 0
    for source in sorted(IMAGE_ROOT.rglob("*")):
        if not source.is_file() or source.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        target = source.with_suffix(".webp")
        before_bytes += source.stat().st_size
        if not target.exists():
            with Image.open(source) as opened:
                image = ImageOps.exif_transpose(opened)
                if image.width > max_width:
                    height = max(1, round(image.height * max_width / image.width))
                    image = image.resize((max_width, height), Image.Resampling.LANCZOS)
                if image.mode not in {"RGB", "RGBA"}:
                    image = image.convert("RGB")
                image.save(target, "WEBP", quality=quality, method=6)
            converted += 1
        after_bytes += target.stat().st_size
        old_url = "/" + source.relative_to(ROOT / "source").as_posix()
        new_url = "/" + target.relative_to(ROOT / "source").as_posix()
        replacements[old_url] = new_url

    if PLACES_PATH.exists() and replacements:
        text = PLACES_PATH.read_text(encoding="utf-8")
        for old_url, new_url in replacements.items():
            text = text.replace(old_url, new_url)
        json.loads(text)
        PLACES_PATH.write_text(text, encoding="utf-8")

    if remove_originals:
        for old_url in replacements:
            original = ROOT / "source" / old_url.lstrip("/")
            if original.exists() and original.with_suffix(".webp").exists():
                original.unlink()
    return {"converted": converted, "before_bytes": before_bytes, "after_bytes": after_bytes}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--remove-originals", action="store_true")
    parser.add_argument("--quality", type=int, default=76)
    parser.add_argument("--max-width", type=int, default=1280)
    args = parser.parse_args()
    print(json.dumps(convert(remove_originals=args.remove_originals, quality=args.quality, max_width=args.max_width)))
