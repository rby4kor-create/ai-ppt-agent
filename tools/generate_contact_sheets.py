"""
Generates assets/previews/contact_sheet.jpg (all images) and one
assets/previews/<category>.jpg per category, so the library can be
visually inspected without opening 200 individual files.

Usage:
    python tools/generate_contact_sheets.py
"""

import json
import os
import sys
from collections import defaultdict

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(ROOT, "assets", "manifest", "image_manifest.json")
PREVIEWS_DIR = os.path.join(ROOT, "assets", "previews")

THUMB_W, THUMB_H = 240, 160
LABEL_H = 34
COLS = 6
PADDING = 8


def build_sheet(images, out_path, title):
    if not images:
        return False

    rows = -(-len(images) // COLS)
    cell_w = THUMB_W + PADDING
    cell_h = THUMB_H + LABEL_H + PADDING
    header_h = 40
    sheet_w = COLS * cell_w + PADDING
    sheet_h = rows * cell_h + PADDING + header_h

    sheet = Image.new("RGB", (sheet_w, sheet_h), (18, 20, 26))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    draw.text((PADDING, 10), f"{title} ({len(images)} images)", fill=(230, 230, 235), font=font)

    for idx, img_entry in enumerate(images):
        row, col = divmod(idx, COLS)
        x = PADDING + col * cell_w
        y = header_h + PADDING + row * cell_h

        path = os.path.join(ROOT, img_entry["relative_path"])
        try:
            with Image.open(path) as im:
                im = im.convert("RGB")
                im.thumbnail((THUMB_W, THUMB_H))
                paste_x = x + (THUMB_W - im.width) // 2
                paste_y = y + (THUMB_H - im.height) // 2
                sheet.paste(im, (paste_x, paste_y))
        except Exception:
            draw.rectangle([x, y, x + THUMB_W, y + THUMB_H], outline=(120, 40, 40))

        label = f"{img_entry['id'][:18]}\nq={img_entry.get('quality_score', '?')}"
        draw.text((x, y + THUMB_H + 2), label, fill=(180, 185, 195), font=font)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    sheet.save(out_path, quality=88)
    return True


def main():
    if not os.path.exists(MANIFEST_PATH):
        print(f"No manifest found at {MANIFEST_PATH}. Run tools/download_images.py first.")
        return 1

    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)
    images = manifest["images"]

    if not images:
        print("Manifest has no images yet - nothing to render.")
        return 0

    build_sheet(images, os.path.join(PREVIEWS_DIR, "contact_sheet.jpg"), "Full Library")
    print(f"Wrote {os.path.join(PREVIEWS_DIR, 'contact_sheet.jpg')} ({len(images)} images)")

    by_category = defaultdict(list)
    for img in images:
        by_category[img.get("category", "uncategorized")].append(img)

    for category, imgs in by_category.items():
        out_path = os.path.join(PREVIEWS_DIR, f"{category}.jpg")
        build_sheet(imgs, out_path, category)
        print(f"Wrote {out_path} ({len(imgs)} images)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
