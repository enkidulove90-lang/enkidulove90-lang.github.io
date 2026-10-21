"""Public, secret-free checks safe to run after a GitHub Pages deployment."""
from __future__ import annotations

import json
import os
import time
import urllib.request

SITE = os.getenv("SITE_BASE_URL", "https://enkidulove90-lang.github.io").rstrip("/")
API = os.getenv("PAPER_INTAKE_API_BASE", "https://paper-intake.enkiduai.club").rstrip("/")


def get(url: str) -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; EnkiduPagesSmoke/1.0)"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        if response.status != 200:
            raise RuntimeError(f"{url}: HTTP {response.status}")
        return response.read()


def main() -> None:
    last_error: Exception | None = None
    for attempt in range(6):
        try:
            get(SITE + "/")
            get(SITE + "/map/")
            payload = json.loads(get(SITE + "/map_data.json"))
            if not isinstance(payload.get("places"), list):
                raise RuntimeError("map_data.json has no places list")
            health = json.loads(get(API + "/health"))
            if health.get("status") != "ok":
                raise RuntimeError("gateway health is not ok")
            print(json.dumps({"status": "ok", "places": len(payload["places"])}))
            return
        except Exception as exc:
            last_error = exc
            if attempt < 5:
                time.sleep(10)
    raise SystemExit(f"post-deploy smoke failed: {last_error}")


if __name__ == "__main__":
    main()
