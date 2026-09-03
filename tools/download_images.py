"""
Builds the local premium visual library (assets/stock/<category>/...) from
config/visual_taxonomy.json, using Pexels as the primary provider and
Unsplash as a secondary provider when a category still needs more images.

Usage:
    python tools/download_images.py                 # fill every category to its target_count
    python tools/download_images.py --category robotics
    python tools/download_images.py --refresh        # re-check counts even if manifest looks complete

Requires PEXELS_API_KEY (recommended) and/or UNSPLASH_ACCESS_KEY in the
environment / .env. If neither is set, this prints a clear setup message
and exits 0 without crashing - existing local assets (if any) keep working
for generation, per the "never block generation on network" requirement.

Every downloaded image is recorded in assets/manifest/image_manifest.json
with full provenance (provider, photographer, source URL, license,
retrieval date) - see models schema in this file's `build_manifest_entry`.
Re-running this script is safe: images already present (by provider+photo_id)
are skipped, so it only tops categories up to their target_count.
"""

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone

import requests
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOCK_DIR = os.path.join(ROOT, "assets", "stock")
MANIFEST_PATH = os.path.join(ROOT, "assets", "manifest", "image_manifest.json")
TAXONOMY_PATH = os.path.join(ROOT, "config", "visual_taxonomy.json")

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "").strip()
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "").strip()

PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"
UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"

MIN_LONG_EDGE = 2000       # "prefer 2000px+, ideally 2400px+"
MIN_QUALITY_SCORE = 0.75   # reject below this, prefer 0.85+


def load_taxonomy():
    with open(TAXONOMY_PATH) as f:
        return json.load(f)


def load_manifest():
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH) as f:
            return json.load(f)
    return {"images": []}


def save_manifest(manifest):
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)


def existing_ids(manifest):
    return {img["id"] for img in manifest["images"]}


def existing_hashes(manifest):
    return {img["sha256"] for img in manifest["images"] if img.get("sha256")}


def compute_quality_score(width, height, provider_relevance_rank):
    """
    Heuristic quality score per the spec's weighted formula:
        technical_quality * 0.20 + composition * 0.25 + relevance * 0.25
        + editorial_quality * 0.20 + presentation_suitability * 0.10

    Composition/editorial/presentation-suitability can't be judged from
    pixels alone without a vision model, so this uses defensible proxies:
      - technical_quality: resolution vs the 2000px/2400px target
      - relevance: the provider's own search rank (result position 1 is
        the API's best match for the query)
      - composition / editorial / presentation_suitability: a flat premium
        default (0.85) - real photography from a curated professional
        provider (Pexels/Unsplash editorial collections), not an
        arbitrary web scrape, so this default is a reasonable prior
        rather than a guess. Manual curation (removing images from the
        contact sheet) is the real quality gate on top of this score.
    """
    long_edge = max(width, height)
    technical_quality = min(1.0, long_edge / 2400)
    relevance = max(0.5, 1.0 - 0.05 * provider_relevance_rank)
    composition = 0.85
    editorial_quality = 0.85
    presentation_suitability = 0.85
    return round(
        technical_quality * 0.20
        + composition * 0.25
        + relevance * 0.25
        + editorial_quality * 0.20
        + presentation_suitability * 0.10,
        3,
    )


def sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def search_pexels(query, per_page=8):
    if not PEXELS_API_KEY:
        return []
    try:
        resp = requests.get(
            PEXELS_SEARCH_URL,
            params={"query": query, "per_page": per_page, "orientation": "landscape", "size": "large"},
            headers={"Authorization": PEXELS_API_KEY},
            timeout=10,
        )
        resp.raise_for_status()
        results = []
        for rank, photo in enumerate(resp.json().get("photos", [])):
            results.append({
                "provider": "pexels",
                "id": f"pexels_{photo['id']}",
                "photo_url": photo["url"],
                "download_url": photo["src"]["large2x"],
                "width": photo["width"],
                "height": photo["height"],
                "photographer": photo.get("photographer", ""),
                "photographer_url": photo.get("photographer_url", ""),
                "rank": rank,
            })
        return results
    except Exception as e:
        print(f"  [pexels] search failed for {query!r}: {e}")
        return []


def search_unsplash(query, per_page=8):
    if not UNSPLASH_ACCESS_KEY:
        return []
    try:
        resp = requests.get(
            UNSPLASH_SEARCH_URL,
            params={"query": query, "per_page": per_page, "orientation": "landscape"},
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
            timeout=10,
        )
        resp.raise_for_status()
        results = []
        for rank, photo in enumerate(resp.json().get("results", [])):
            results.append({
                "provider": "unsplash",
                "id": f"unsplash_{photo['id']}",
                "photo_url": photo["links"]["html"],
                "download_url": photo["urls"]["regular"],
                "width": photo["width"],
                "height": photo["height"],
                "photographer": photo.get("user", {}).get("name", ""),
                "photographer_url": photo.get("user", {}).get("links", {}).get("html", ""),
                "rank": rank,
            })
        return results
    except Exception as e:
        print(f"  [unsplash] search failed for {query!r}: {e}")
        return []


def download_one(candidate, category, index, seen_ids, seen_hashes):
    if candidate["id"] in seen_ids:
        return None
    if max(candidate["width"], candidate["height"]) < MIN_LONG_EDGE:
        return None

    quality_score = compute_quality_score(candidate["width"], candidate["height"], candidate["rank"])
    if quality_score < MIN_QUALITY_SCORE:
        return None

    cat_dir = os.path.join(STOCK_DIR, category)
    os.makedirs(cat_dir, exist_ok=True)
    filename = f"{category}_{index:03d}.jpg"
    filepath = os.path.join(cat_dir, filename)

    try:
        resp = requests.get(candidate["download_url"], timeout=20)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            f.write(resp.content)
        with Image.open(filepath) as im:
            im.verify()
    except Exception as e:
        print(f"  download failed for {candidate['id']}: {e}")
        if os.path.exists(filepath):
            os.remove(filepath)
        return None

    digest = sha256_of_file(filepath)
    if digest in seen_hashes:
        os.remove(filepath)
        return None

    entry = {
        "id": candidate["id"],
        "filename": filename,
        "relative_path": os.path.join("assets", "stock", category, filename),
        "provider": candidate["provider"],
        "source_url": candidate["photo_url"],
        "photographer": candidate["photographer"],
        "photographer_url": candidate.get("photographer_url", ""),
        "license": "Pexels License (free to use)" if candidate["provider"] == "pexels" else "Unsplash License (free to use)",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "category": category,
        "tags": [],
        "orientation": "landscape" if candidate["width"] >= candidate["height"] else "portrait",
        "width": candidate["width"],
        "height": candidate["height"],
        "aspect_ratio": round(candidate["width"] / candidate["height"], 3),
        "quality_score": quality_score,
        "sha256": digest,
        "usage": ["topic_slide"],
    }
    seen_ids.add(entry["id"])
    seen_hashes.add(digest)
    return entry


def fill_category(category, cfg, manifest, seen_ids, seen_hashes):
    current = [img for img in manifest["images"] if img["category"] == category]
    target = cfg.get("target_count", 12)
    needed = max(0, target - len(current))
    if needed == 0:
        print(f"[{category}] already at target ({len(current)}/{target})")
        return 0

    print(f"[{category}] have {len(current)}/{target}, fetching {needed} more...")
    added = 0
    next_index = len(current) + 1

    queries = cfg.get("preferred_queries", [cfg.get("label", category)])
    for query in queries:
        if added >= needed:
            break
        candidates = search_pexels(query) or search_unsplash(query)
        for candidate in candidates:
            if added >= needed:
                break
            entry = download_one(candidate, category, next_index, seen_ids, seen_hashes)
            if entry:
                manifest["images"].append(entry)
                added += 1
                next_index += 1
                print(f"  + {entry['filename']} (q={entry['quality_score']}, {entry['provider']})")
            time.sleep(0.2)  # be polite to the API

    if added < needed:
        print(f"  [{category}] only found {added}/{needed} more "
              f"(now {len(current) + added}/{target}) - will retry on next run")
    return added


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", help="Only fill this one category")
    parser.add_argument("--refresh", action="store_true", help="Re-check all categories even if manifest looks complete")
    args = parser.parse_args()

    if not PEXELS_API_KEY and not UNSPLASH_ACCESS_KEY:
        print(
            "No PEXELS_API_KEY or UNSPLASH_ACCESS_KEY found in the environment/.env.\n"
            "The image library cannot be downloaded without one of these.\n\n"
            "Setup:\n"
            "  1. Get a free key at https://www.pexels.com/api/ (preferred) and/or\n"
            "     https://unsplash.com/developers\n"
            "  2. Add it to .env:  PEXELS_API_KEY=your_key_here\n"
            "  3. Re-run: python tools/download_images.py\n\n"
            "Generation will continue to work with whatever is already in "
            "assets/stock/ (or the static per-category fallback images) "
            "until then - this is not a fatal error."
        )
        return 0

    taxonomy = load_taxonomy()
    manifest = load_manifest()
    seen_ids = existing_ids(manifest)
    seen_hashes = existing_hashes(manifest)

    categories = [args.category] if args.category else list(taxonomy.keys())
    total_added = 0
    for category in categories:
        if category not in taxonomy:
            print(f"Unknown category: {category}")
            continue
        total_added += fill_category(category, taxonomy[category], manifest, seen_ids, seen_hashes)
        save_manifest(manifest)  # save after every category so a failure mid-run doesn't lose progress

    print(f"\nDone. Added {total_added} new images. Library now has {len(manifest['images'])} total.")
    print(f"Manifest: {MANIFEST_PATH}")
    if len(manifest["images"]) < 200:
        print(f"NOTE: library is below the 200-image target ({len(manifest['images'])}/200). "
              f"Re-run this script (API rate limits may have capped this run) to keep filling it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
