"""
Validates the image library against the project's QA bar and writes
qa/image_library_report.md (+ .json). Run after tools/download_images.py
and tools/deduplicate_images.py.

Usage:
    python tools/validate_images.py
"""

import json
import os
import sys
from collections import defaultdict

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(ROOT, "assets", "manifest", "image_manifest.json")
QA_DIR = os.path.join(ROOT, "qa")

REQUIRED_FIELDS = [
    "id", "filename", "relative_path", "provider", "source_url", "photographer",
    "license", "retrieved_at", "category", "width", "height", "quality_score",
]
MIN_LONG_EDGE = 2000
TARGET_TOTAL = 200


def main():
    if not os.path.exists(MANIFEST_PATH):
        print(f"No manifest found at {MANIFEST_PATH}. Run tools/download_images.py first.")
        return 1

    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)
    images = manifest["images"]

    by_category = defaultdict(list)
    invalid = []
    missing_metadata = []
    low_res = []
    missing_source = []
    broken = []
    quality_scores = []
    provider_counts = defaultdict(int)
    seen_hashes = set()
    dup_count = 0

    for img in images:
        by_category[img.get("category", "uncategorized")].append(img)
        provider_counts[img.get("provider", "unknown")] += 1

        missing = [f for f in REQUIRED_FIELDS if not img.get(f)]
        if missing:
            missing_metadata.append((img.get("id", "?"), missing))

        if not img.get("source_url"):
            missing_source.append(img.get("id", "?"))

        path = os.path.join(ROOT, img.get("relative_path", ""))
        if not os.path.exists(path):
            broken.append(img.get("id", "?"))
            invalid.append(img.get("id", "?"))
            continue

        try:
            with Image.open(path) as im:
                im.verify()
                w, h = img.get("width", 0), img.get("height", 0)
        except Exception:
            broken.append(img.get("id", "?"))
            invalid.append(img.get("id", "?"))
            continue

        if max(w, h) < MIN_LONG_EDGE:
            low_res.append(img.get("id", "?"))

        sha = img.get("sha256")
        if sha:
            if sha in seen_hashes:
                dup_count += 1
            seen_hashes.add(sha)

        if isinstance(img.get("quality_score"), (int, float)):
            quality_scores.append(img["quality_score"])

    total = len(images)
    valid = total - len(invalid)
    avg_quality = round(sum(quality_scores) / len(quality_scores), 3) if quality_scores else 0.0

    lines = []
    lines.append("# IMAGE LIBRARY QA\n")
    lines.append(f"Total images: {total}\n")
    lines.append("## Categories\n")
    for cat, imgs in sorted(by_category.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"- {cat}: {len(imgs)}")
    lines.append("")
    lines.append(f"Valid: {valid}")
    lines.append(f"Invalid / broken: {len(invalid)}")
    lines.append(f"Duplicates (by SHA256): {dup_count}")
    lines.append(f"Low resolution (< {MIN_LONG_EDGE}px long edge): {len(low_res)}")
    lines.append(f"Missing source URLs: {len(missing_source)}")
    lines.append(f"Missing required metadata: {len(missing_metadata)}")
    lines.append("")
    lines.append(f"Average quality score: {avg_quality}")
    lines.append("")
    lines.append("## Provider breakdown")
    for provider, count in sorted(provider_counts.items(), key=lambda kv: -kv[1]):
        lines.append(f"- {provider}: {count}")
    lines.append("")
    lines.append(f"## Target check")
    lines.append(f"Minimum library requirement: {TARGET_TOTAL}")
    lines.append(f"Status: {'MET' if total >= TARGET_TOTAL else f'BELOW TARGET (need {TARGET_TOTAL - total} more)'}")

    if missing_metadata:
        lines.append("\n## Images missing required fields")
        for img_id, missing in missing_metadata[:30]:
            lines.append(f"- {img_id}: missing {missing}")

    if broken:
        lines.append("\n## Broken / unreadable images")
        for img_id in broken[:30]:
            lines.append(f"- {img_id}")

    report_md = "\n".join(lines)

    os.makedirs(QA_DIR, exist_ok=True)
    with open(os.path.join(QA_DIR, "image_library_report.md"), "w") as f:
        f.write(report_md + "\n")

    report_json = {
        "total": total,
        "valid": valid,
        "invalid": len(invalid),
        "duplicates": dup_count,
        "low_resolution": len(low_res),
        "missing_source_urls": len(missing_source),
        "missing_metadata": len(missing_metadata),
        "average_quality_score": avg_quality,
        "categories": {cat: len(imgs) for cat, imgs in by_category.items()},
        "providers": dict(provider_counts),
        "target_total": TARGET_TOTAL,
        "meets_target": total >= TARGET_TOTAL,
    }
    with open(os.path.join(QA_DIR, "image_library_report.json"), "w") as f:
        json.dump(report_json, f, indent=2)

    print(report_md)
    print(f"\nSaved to qa/image_library_report.md and qa/image_library_report.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
