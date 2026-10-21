"""Publish a local commit through GitHub's Git Data API when Git TLS is broken."""
from __future__ import annotations

import argparse
import base64
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]


def token() -> str:
    return subprocess.check_output(["gh", "auth", "token"], text=True).strip()


def request(method: str, url: str, auth: str, payload: dict | None = None) -> dict:
    headers = {"Authorization": f"Bearer {auth}", "Accept": "application/vnd.github+json", "User-Agent": "enkidu-git-fallback"}
    for attempt, delay in enumerate((1, 2, 4, 0)):
        response = requests.request(method, url, headers=headers, json=payload, timeout=120)
        if response.ok:
            return response.json()
        if response.status_code not in {429, 500, 502, 503, 504} or attempt == 3:
            raise RuntimeError(f"GitHub API {method} {url}: HTTP {response.status_code} {response.text[:300]}")
        time.sleep(delay)
    raise RuntimeError("unreachable")


def changed_paths(base: str) -> tuple[list[str], list[str]]:
    output = subprocess.check_output(["git", "diff", "--name-status", "-z", base, "HEAD"], cwd=ROOT)
    fields = output.decode("utf-8").split("\0")
    uploads: list[str] = []
    deletes: list[str] = []
    index = 0
    while index < len(fields) - 1:
        status = fields[index]
        index += 1
        if status.startswith("R"):
            deletes.append(fields[index]); uploads.append(fields[index + 1]); index += 2
        else:
            path = fields[index]; index += 1
            (deletes if status.startswith("D") else uploads).append(path)
    return uploads, deletes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--branch", default="source")
    parser.add_argument("--base", required=True, help="local ancestor used to select changed paths")
    args = parser.parse_args()
    auth = token()
    api = f"https://api.github.com/repos/{args.repository}"
    ref = request("GET", f"{api}/git/ref/heads/{args.branch}", auth)
    parent = ref["object"]["sha"]
    commit = request("GET", f"{api}/git/commits/{parent}", auth)
    uploads, deletes = changed_paths(args.base)

    def upload(path: str) -> dict:
        content = base64.b64encode((ROOT / path).read_bytes()).decode("ascii")
        blob = request("POST", f"{api}/git/blobs", auth, {"content": content, "encoding": "base64"})
        return {"path": path.replace("\\", "/"), "mode": "100644", "type": "blob", "sha": blob["sha"]}

    entries: list[dict] = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {executor.submit(upload, path): path for path in uploads}
        for count, future in enumerate(as_completed(futures), 1):
            entries.append(future.result())
            if count % 25 == 0:
                print(f"uploaded {count}/{len(uploads)} blobs")
    entries.extend({"path": path.replace("\\", "/"), "mode": "100644", "type": "blob", "sha": None} for path in deletes)
    tree = request("POST", f"{api}/git/trees", auth, {"base_tree": commit["tree"]["sha"], "tree": entries})
    message = subprocess.check_output(["git", "log", "-1", "--pretty=%B"], cwd=ROOT, text=True).strip()
    created = request("POST", f"{api}/git/commits", auth, {"message": message, "tree": tree["sha"], "parents": [parent]})
    request("PATCH", f"{api}/git/refs/heads/{args.branch}", auth, {"sha": created["sha"], "force": False})
    print(json.dumps({"status": "pushed", "commit": created["sha"], "files": len(entries)}))


if __name__ == "__main__":
    main()
