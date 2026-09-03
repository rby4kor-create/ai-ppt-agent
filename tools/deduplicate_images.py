"""
Removes near-duplicate images from the visual library using perceptual
hashing (on top of the exact-duplicate SHA256 check already done at
download time in tools/download_images.py). Two images can be
byte-different (different crop/compression from the same source photo,
or two providers returning the same stock photo) yet visually near-
identical - phash catches those; SHA256 does not.

Usage:
    python tools/deduplicate_images.py            # dry run, reports only
    python tools/deduplicate_images.py --apply    # actually delete + update manifest
"""

import argparse
import json
import os
import sys

import imagehash
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(ROOT, "assets", "manifest", "image_manifest.json")

HASH_DISTANCE_THRESHOLD = 6  # <=6 bits different on a 64-bit phash = "near-identical"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Actually remove duplicates (default is dry-run)")
    args = parser.parse_args()

    if not os.path.exists(MANIFEST_PATH):
        print(f"No manifest found at {MANIFEST_PATH} - nothing to deduplicate.")
        return 0

    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    images = manifest["images"]
    hashes = {}
    for img in images:
        path = os.path.join(ROOT, img["relative_path"])
        if not os.path.exists(path):
            continue
        try:
            with Image.open(path) as im:
                hashes[img["id"]] = imagehash.phash(im)
        except Exception as e:
            print(f"Could not hash {img['id']}: {e}")

    to_remove = set()
    ids = list(hashes.keys())
    by_id = {img["id"]: img for img in images}

    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            a, b = ids[i], ids[j]
            if a in to_remove or b in to_remove:
                continue
            distance = hashes[a] - hashes[b]
            if distance <= HASH_DISTANCE_THRESHOLD:
                # keep the higher quality_score, drop the other
                worse = a if by_id[a]["quality_score"] <= by_id[b]["quality_score"] else b
                to_remove.add(worse)
                print(f"Near-duplicate (distance={distance}): keeping "
                      f"{b if worse == a else a}, dropping {worse}")

    if not to_remove:
        print("No near-duplicates found.")
        return 0

    print(f"\n{len(to_remove)} near-duplicate(s) found.")
    if not args.apply:
        print("Dry run only - re-run with --apply to actually remove them.")
        return 0

    remaining = []
    for img in images:
        if img["id"] in to_remove:
            path = os.path.join(ROOT, img["relative_path"])
            if os.path.exists(path):
                os.remove(path)
        else:
            remaining.append(img)

    manifest["images"] = remaining
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Removed {len(to_remove)} duplicates. Library now has {len(remaining)} images.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
