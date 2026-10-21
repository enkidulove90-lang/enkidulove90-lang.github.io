"""Merge the latest remote places.json while preserving local WebP references."""
from __future__ import annotations

import base64
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "source" / "_data" / "places.json"
REPOSITORY = "enkidulove90-lang/enkidulove90-lang.github.io"

raw = subprocess.check_output(
    ["gh", "api", f"repos/{REPOSITORY}/contents/source/_data/places.json?ref=source", "--jq", ".content"],
    text=True,
)
text = base64.b64decode("".join(raw.split())).decode("utf-8")
for source in (ROOT / "source" / "images" / "map").glob("*.webp"):
    jpg = "/images/map/" + source.with_suffix(".jpg").name
    jpeg = "/images/map/" + source.with_suffix(".jpeg").name
    webp = "/images/map/" + source.name
    text = text.replace(jpg, webp).replace(jpeg, webp)
json.loads(text)
TARGET.write_text(text, encoding="utf-8")
print(f"merged {TARGET}")
