#!/usr/bin/env python3
"""Build the paper map from local WGS-84 data, with opt-in Nominatim lookup."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import time
import unicodedata
from datetime import datetime, timezone

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
POSTS = ROOT / "source" / "_posts"
OUTPUT = ROOT / "source" / "_data" / "places.json"
IMAGE_DIR = ROOT / "source" / "images" / "map"
DICTIONARIES = ROOT / "tools" / "location_dict.json"
AFFILIATIONS = ROOT / "tools" / "paper_affiliations.json"
NOMINATIM_SEARCH = os.environ.get("NOMINATIM_URL", "https://nominatim.openstreetmap.org/search")
WIKIMEDIA_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "EnkiduRecSysFrontier/1.1 (paper-map; https://enkidulove90-lang.github.io/)"


def parse_scalar(value: str):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        return [parse_scalar(item) for item in value[1:-1].split(",") if item.strip()]
    return value


def parse_frontmatter(raw: str) -> dict:
    if not raw.startswith("---"):
        return {}
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}
    result = {}
    for line in parts[1].splitlines():
        match = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if match:
            result[match.group(1)] = parse_scalar(match.group(2))
    return result


def normalized_name(value: str) -> str:
    return re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", unicodedata.normalize("NFKC", str(value)).casefold()).strip()


def load_dictionaries(path: pathlib.Path = DICTIONARIES) -> dict:
    if not path.exists():
        return {"institutions": {}, "publishers": {}, "cities": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    result = {"institutions": {}, "publishers": {}, "cities": {}}
    for section in result:
        for key, value in data.get(section, {}).items():
            result[section][normalized_name(key)] = value
    return result


def load_affiliation_overrides(path: pathlib.Path = AFFILIATIONS) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8")).get("papers", {})


def apply_affiliation_override(metadata: dict, overrides: dict) -> dict:
    slug = str(metadata.get("slug") or "")
    override = overrides.get(slug)
    if not override or any(metadata.get(field) for field in ("affiliation_name", "affil_city", "venue_city")):
        return metadata
    return {**metadata, **{key: value for key, value in override.items() if value not in (None, "")}}


def find_dictionary_entry(name: str, dictionaries: dict, sections=("institutions", "publishers")) -> dict | None:
    needle = normalized_name(name)
    if not needle:
        return None
    for section in sections:
        for key, entry in dictionaries.get(section, {}).items():
            aliases = [key, entry.get("name", ""), *entry.get("aliases", [])]
            normalized_aliases = {normalized_name(alias) for alias in aliases if alias}
            comparable = normalized_aliases | {alias.removeprefix("the ") for alias in normalized_aliases}
            if needle in comparable or any(len(alias) >= 8 and alias in needle for alias in comparable):
                return entry
    return None


def static_city_coordinates(city: str, dictionaries: dict) -> tuple[float, float] | None:
    value = dictionaries.get("cities", {}).get(normalized_name(city), {})
    coordinates = value.get("wgs84") if isinstance(value, dict) else None
    if not isinstance(coordinates, list) or len(coordinates) != 2:
        return None
    return float(coordinates[0]), float(coordinates[1])


def select_coordinates(record: dict, city: str, dictionaries: dict, cached: dict | None):
    return record.get("wgs84") or static_city_coordinates(city, dictionaries) or (cached or {}).get("wgs84")


def city_description(city: str, dictionaries: dict) -> str:
    value = dictionaries.get("cities", {}).get(normalized_name(city), {})
    return str(value.get("description") or f"{city}：论文、机构与城市在这里相遇。")


def city_presentation(city: str, dictionaries: dict, image_count: int = 0) -> dict:
    value = dictionaries.get("cities", {}).get(normalized_name(city), {})
    description = str(value.get("description") or f"{city}：论文、机构与城市在这里相遇。")
    images = [str(item) for item in value.get("city_images", []) if str(item).startswith("/images/map/")]
    target_count = max(image_count, len(images))
    if target_count and len(images) < target_count:
        slug = slugify_city(city)
        generated = [f"/images/map/{slug}{'' if index == 1 else f'-{index}'}.jpg"
                     for index in range(1, target_count + 1)]
        images = list(dict.fromkeys([*images, *generated]))[:target_count]
    return {
        "hover_text": str(value.get("hover_text") or description.split("。", 1)[0]),
        "description": description,
        "city_images": list(dict.fromkeys(images)),
    }


def institution_profile(entry: dict, fallback_name: str, city: str) -> dict:
    name = str(entry.get("name") or fallback_name or city)
    return {
        "name": name,
        "kind": str(entry.get("kind") or "affiliation"),
        "description": str(entry.get("inst_desc") or f"{name} 是位于 {city} 的科研机构。"),
    }


def first_city(value) -> str:
    if isinstance(value, list):
        return next((str(item).strip() for item in value if str(item).strip()), "")
    return str(value or "").strip()


def affiliation_kind(name: str, dictionaries: dict) -> str:
    entry = find_dictionary_entry(name, dictionaries, ("institutions",))
    return str(entry.get("kind") or "affiliation") if entry else "affiliation"


def resolve_location(metadata: dict, dictionaries: dict) -> dict | None:
    """Resolve semantic location from explicit fields and trusted local aliases."""
    requested = str(metadata.get("location_type") or "").strip().casefold()
    affiliation = str(metadata.get("affiliation_name") or "").strip()
    corresponding = first_city(metadata.get("corresponding_city"))
    venue = first_city(metadata.get("venue_city"))
    affiliation_city = first_city(metadata.get("affil_city"))
    entry = find_dictionary_entry(affiliation, dictionaries)
    if requested == "virtual":
        return {"city": "Virtual", "location_type": "virtual", "location_label": "线上空间", "source": "virtual"}
    if requested == "venue" and venue:
        return {"city": venue, "location_type": "venue", "location_label": metadata.get("venue_name") or venue, "source": "venue_city"}
    if requested in ("affiliation", "school", "company"):
        if entry:
            return {"city": entry.get("city") or affiliation_city, "location_type": entry.get("kind") or requested,
                    "location_label": entry.get("name") or affiliation, "source": "location_dictionary",
                    "wgs84": entry.get("wgs84"), "place_key": entry.get("name") or affiliation,
                    "institution": institution_profile(entry, affiliation, entry.get("city") or affiliation_city)}
        if affiliation_city:
            return {"city": affiliation_city, "location_type": requested if requested != "affiliation" else "affiliation",
                    "location_label": affiliation or affiliation_city, "source": "affil_city"}
        if affiliation and metadata.get("first_author"):
            return {"city": affiliation, "location_type": requested if requested != "affiliation" else "school",
                    "location_label": affiliation, "source": "verified_first_author_affiliation",
                    "institution": {"name": affiliation, "kind": requested,
                                    "description": f"论文第一作者 {metadata.get('first_author')} 的署名机构。"}}
    if requested == "publisher" and entry:
        return {"city": entry.get("city"), "location_type": "publisher", "location_label": entry.get("name") or affiliation,
                "source": "location_dictionary", "wgs84": entry.get("wgs84"), "place_key": entry.get("name") or affiliation,
                "institution": institution_profile(entry, affiliation, entry.get("city"))}
    if not requested:
        if venue:
            return {"city": venue, "location_type": "venue", "location_label": metadata.get("venue_name") or venue, "source": "venue_city"}
        if entry:
            return {"city": entry.get("city"), "location_type": entry.get("kind") or "affiliation",
                    "location_label": entry.get("name") or affiliation, "source": "location_dictionary",
                    "wgs84": entry.get("wgs84"), "place_key": entry.get("name") or affiliation,
                    "institution": institution_profile(entry, affiliation, entry.get("city"))}
        if affiliation_city:
            return {"city": affiliation_city, "location_type": "affiliation",
                    "location_label": affiliation or affiliation_city, "source": "affil_city"}
    if corresponding:
        kind = requested if requested in ("venue", "school", "company", "publisher", "affiliation") else "affiliation"
        return {"city": corresponding, "location_type": kind, "location_label": affiliation or corresponding,
                "source": "corresponding_city"}
    return None


def slugify_city(city: str) -> str:
    normalized = unicodedata.normalize("NFKD", city).encode("ascii", "ignore").decode().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return slug or "place-" + hashlib.sha1(city.encode("utf-8")).hexdigest()[:10]


def reusable_cached_place(city: str, cached: dict | None, root: pathlib.Path = ROOT):
    if not cached or cached.get("name", "").casefold() != city.casefold():
        return None
    image = str(cached.get("image", ""))
    image_path = root / "source" / image.lstrip("/").replace("/", os.sep)
    required = cached.get("wgs84") and image.startswith("/images/map/")
    return cached if required and image_path.exists() else None


def request_json(session: requests.Session, url: str, params: dict):
    response = session.get(url, params=params, timeout=45)
    response.raise_for_status()
    return response.json()


def first_nominatim_coordinate(results: list[dict]) -> tuple[float, float] | None:
    if not results:
        return None
    return float(results[0]["lon"]), float(results[0]["lat"])


def nominatim_geocode(session: requests.Session, query: str, endpoint: str = NOMINATIM_SEARCH) -> tuple[float, float] | None:
    results = request_json(session, endpoint, {"q": query, "format": "jsonv2", "limit": 1, "addressdetails": 1})
    return first_nominatim_coordinate(results)


def wikimedia_image_candidates(pages: list[dict], city: str, limit: int = 3,
                               excluded_urls: set[str] | None = None,
                               excluded_titles: set[str] | None = None) -> list[tuple[str, str]]:
    landscape_terms = ("skyline", "cityscape", "panorama", "aerial", "harbour", "harbor", "downtown")
    pages.sort(key=lambda page: (
        city.casefold() not in page.get("title", "").casefold(),
        not any(term in page.get("title", "").casefold() for term in landscape_terms),
        page.get("index", 999),
    ))
    candidates, seen = [], set(excluded_urls or set())
    for page in pages:
        if page.get("title", "") in (excluded_titles or set()):
            continue
        info = (page.get("imageinfo") or [{}])[0]
        url = info.get("thumburl") or info.get("url")
        if url and url not in seen:
            seen.add(url)
            candidates.append((url, page.get("title", "")))
        if len(candidates) >= limit:
            break
    return candidates


def wikimedia_gallery_queries(city: str) -> list[str]:
    return [
        f'"{city}" street life',
        f'"{city}" people culture',
        f'"{city}" nature park',
        f'"{city}" public art architecture',
        f'"{city}" skyline cityscape',
    ]


def wikimedia_thumbnails(session: requests.Session, city: str, lng: float, lat: float,
                         limit: int = 5, excluded_urls: set[str] | None = None,
                         excluded_titles: set[str] | None = None) -> list[tuple[str, str]]:
    candidates, seen = [], set(excluded_urls or set())
    for query in wikimedia_gallery_queries(city)[:limit]:
        search = request_json(session, WIKIMEDIA_API, {"action": "query", "format": "json", "generator": "search",
            "gsrsearch": query, "gsrnamespace": 6, "gsrlimit": 18,
            "prop": "imageinfo", "iiprop": "url", "iiurlwidth": 1280})
        pages = list((search.get("query", {}).get("pages") or {}).values())
        for candidate in wikimedia_image_candidates(pages, city, 6, seen, excluded_titles):
            if candidate[0] not in seen:
                seen.add(candidate[0])
                candidates.append(candidate)
                break
    if len(candidates) < limit:
        nearby = request_json(session, WIKIMEDIA_API, {"action": "query", "format": "json", "generator": "geosearch",
            "ggsprimary": "all", "ggsnamespace": 6, "ggsradius": 10000, "ggslimit": 20, "ggscoord": f"{lat}|{lng}",
            "prop": "imageinfo", "iiprop": "url", "iiurlwidth": 1280})
        for candidate in wikimedia_image_candidates(
                list((nearby.get("query", {}).get("pages") or {}).values()), city, limit, seen, excluded_titles):
            if candidate[0] not in seen:
                seen.add(candidate[0])
                candidates.append(candidate)
            if len(candidates) >= limit:
                break
    if not candidates:
        raise RuntimeError(f"Wikimedia image not found for {city}")
    return candidates


def wikimedia_thumbnail(session: requests.Session, city: str, lng: float, lat: float) -> tuple[str, str]:
    return wikimedia_thumbnails(session, city, lng, lat, 1)[0]


def download_image(session: requests.Session, url: str, destination: pathlib.Path) -> None:
    response = session.get(url, timeout=90)
    response.raise_for_status()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(response.content)


def unique_local_images(paths: list[pathlib.Path]) -> list[pathlib.Path]:
    unique, hashes = [], set()
    for path in paths:
        if not path.exists():
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in hashes:
            continue
        hashes.add(digest)
        unique.append(path)
    return unique


def load_location_records(dictionaries: dict | None = None) -> list[dict]:
    dictionaries = dictionaries or load_dictionaries()
    overrides = load_affiliation_overrides()
    records = []
    for post in POSTS.glob("*.md"):
        metadata = parse_frontmatter(post.read_text(encoding="utf-8"))
        metadata = apply_affiliation_override(metadata, overrides)
        resolved = resolve_location(metadata, dictionaries)
        if resolved:
            records.append({"paper_id": str(metadata.get("slug") or post.stem),
                            "title": str(metadata.get("title") or post.stem),
                            "first_author": str(metadata.get("first_author") or ""),
                            "country": str(metadata.get("country") or ""), **resolved})
    return records


def load_existing() -> dict:
    if not OUTPUT.exists():
        return {"places": [], "assignments": []}
    return json.loads(OUTPUT.read_text(encoding="utf-8"))


def virtual_place(dictionaries: dict) -> dict:
    presentation = city_presentation("Virtual", dictionaries)
    return {"id": "virtual", "name": "线上空间", "city": "Virtual", "wgs84": [0.0, 20.0],
            "image": "/images/map/virtual.svg", "image_source": "local illustration",
            "hover_text": presentation["hover_text"], "city_images": ["/images/map/virtual.svg"],
            "description": presentation["description"], "updated_at": datetime.now(timezone.utc).isoformat()}


def build_places(dry_run: bool = False, resolve_missing: bool = False, refresh_gallery: bool = False) -> dict:
    dictionaries = load_dictionaries()
    records = load_location_records(dictionaries)
    existing_places = load_existing().get("places", [])
    existing_by_id = {item.get("id"): item for item in existing_places}
    existing_by_city = {item.get("name", "").casefold(): item for item in existing_places}
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    places_by_id, missing = {}, []
    record_counts = {}
    for record in records:
        record_counts[record["city"]] = record_counts.get(record["city"], 0) + 1
    used_image_urls = set()
    for record in records:
        gallery = []
        if record["city"] == "Virtual":
            places_by_id["virtual"] = virtual_place(dictionaries)
            continue
        place_id = slugify_city(record.get("place_key") or record["city"])
        if place_id in places_by_id:
            continue
        cached = existing_by_id.get(place_id) or existing_by_city.get(record["city"].casefold())
        coordinates = select_coordinates(record, record["city"], dictionaries, cached)
        if not coordinates and resolve_missing:
            coordinates = nominatim_geocode(session, record.get("location_label") or record["city"])
            time.sleep(1.1)
        if not coordinates:
            missing.append({"paper_id": record["paper_id"], "query": record.get("location_label") or record["city"], "reason": "no trusted coordinate"})
            continue
        image = cached.get("image") if cached else f"/images/map/{slugify_city(record['city'])}.jpg"
        image_path = ROOT / "source" / image.lstrip("/").replace("/", os.sep)
        image_source = cached.get("image_source", "local cache") if cached else "local cache"
        if not image_path.exists() and resolve_missing:
            image_url, image_source = wikimedia_thumbnail(session, record["city"], *coordinates)
            image = f"/images/map/{slugify_city(record['city'])}.jpg"
            image_path = ROOT / "source" / image.lstrip("/")
            download_image(session, image_url, image_path)
        if not image_path.exists():
            missing.append({"paper_id": record["paper_id"], "query": record["city"], "reason": "local image missing"})
            continue
        presentation = city_presentation(record["city"], dictionaries, max(5, record_counts[record["city"]]))
        if (resolve_missing or refresh_gallery) and presentation["city_images"]:
            target_paths = [ROOT / "source" / item.lstrip("/").replace("/", os.sep)
                            for item in presentation["city_images"]]
            if refresh_gallery or any(not path.exists() for path in target_paths):
                gallery = wikimedia_thumbnails(
                    session, record["city"], *coordinates, len(target_paths), excluded_urls=used_image_urls,
                    excluded_titles={image_source}
                )
                used_image_urls.update(item[0] for item in gallery)
                for target, (image_url, _) in zip(target_paths, gallery):
                    if refresh_gallery or not target.exists():
                        download_image(session, image_url, target)
                time.sleep(1.1)
        candidate_images = list(dict.fromkeys([image, *presentation["city_images"]]))
        candidate_paths = [ROOT / "source" / item.lstrip("/").replace("/", os.sep) for item in candidate_images]
        unique_paths = unique_local_images(candidate_paths)
        city_images = ["/" + path.relative_to(ROOT / "source").as_posix() for path in unique_paths]
        places_by_id[place_id] = {"id": place_id, "name": record["city"], "city": record["city"],
            "wgs84": [float(coordinates[0]), float(coordinates[1])], "image": image, "image_source": image_source,
            "hover_image": image, "hover_text": presentation["hover_text"], "city_images": city_images,
            "image_sources": [source for _, source in gallery] or [image_source],
            "institution": record.get("institution"), "description": presentation["description"],
            "updated_at": datetime.now(timezone.utc).isoformat()}
    assignments = []
    for record in records:
        place_id = "virtual" if record["city"] == "Virtual" else slugify_city(record.get("place_key") or record["city"])
        if place_id in places_by_id:
            assignments.append({"paper_id": record["paper_id"], "place_id": place_id,
                "location_type": record["location_type"], "location_label": record["location_label"], "source": record["source"]})
    payload = {"generated": datetime.now(timezone.utc).isoformat(), "places": list(places_by_id.values()),
               "assignments": assignments, "missing": missing}
    if not dry_run:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="report without writing")
    parser.add_argument("--resolve-missing", action="store_true", help="opt in to rate-limited Nominatim/Wikimedia requests")
    parser.add_argument("--refresh-gallery", action="store_true", help="replace city galleries with diverse Wikimedia views")
    args = parser.parse_args()
    result = build_places(args.dry_run, args.resolve_missing, args.refresh_gallery)
    print(json.dumps({"places": len(result["places"]), "assignments": len(result["assignments"]), "missing": result["missing"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
