"""
generate_placeholder_library.py

Generates a LOCAL, on-brand placeholder image library used until real
licensed photography is downloaded via tools/download_images.py (which
needs a real internet connection + API key, not available in this
sandbox).

Design intent: these are clean, editorial, blue/charcoal/white
compositions in the CW23/CW28 visual language. They are intentionally
NOT meant to look like final photography — they exist so the deck can
be built, rendered, and QA'd end-to-end today. Swapping in real photos
later requires zero code changes: same folders, same filenames pattern,
same aspect ratio.

Hard rule enforced here: no red, no "glowing brain", no generic
particle-network clichés anywhere in this generator.
"""

import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

# ---- palette (matches theme.py) ----
INK = (32, 40, 50)          # #202832 charcoal text
MUTE = (91, 102, 117)       # #5B6675
FAINT = (217, 225, 234)     # light divider
BLUE = (23, 107, 255)       # #176BFF primary accent
BLUE_DEEP = (13, 71, 179)
BLUE_PALE = (223, 235, 255)
PAPER = (248, 250, 252)
WHITE = (255, 255, 255)

W, H = 2400, 1600  # 3:2 landscape, 2400px+ per spec

CATEGORY_STYLES = {
    "frontier_ai": "lab_grid",
    "agentic_ai": "flow_nodes",
    "developer_ai": "code_lines",
    "enterprise_ai": "dash_panels",
    "infrastructure": "server_rows",
    "hardware": "chip_grid",
    "robotics": "arm_silhouette",
    "healthcare": "pulse_line",
    "cybersecurity": "shield_grid",
    "climate_ai": "contour_waves",
    "creative_ai": "brush_strokes",
    "economics": "bar_ascend",
    "speech_ai": "waveform",
    "multimodal": "layered_frames",
    "governance": "balance_scale",
}

random.seed(7)


def base_canvas(seed):
    rnd = random.Random(seed)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    # subtle vertical gradient toward white
    for y in range(H):
        t = y / H
        r = int(PAPER[0] + (WHITE[0] - PAPER[0]) * t)
        g = int(PAPER[1] + (WHITE[1] - PAPER[1]) * t)
        b = int(PAPER[2] + (WHITE[2] - PAPER[2]) * t)
        d.line([(0, y), (W, y)], fill=(r, g, b))
    return img, d, rnd


def lab_grid(seed):
    img, d, rnd = base_canvas(seed)
    # research-lab feel: fine grid + a few emphasized blue nodes (data points, not a "brain")
    step = 90
    for x in range(0, W, step):
        d.line([(x, 0), (x, H)], fill=(*FAINT, ), width=1)
    for y in range(0, H, step):
        d.line([(0, y), (W, y)], fill=(*FAINT, ), width=1)
    pts = [(rnd.randint(200, W - 200), rnd.randint(200, H - 200)) for _ in range(9)]
    for (x, y) in pts:
        d.ellipse([x - 6, y - 6, x + 6, y + 6], fill=BLUE)
    # connect a few nearest pairs, thin lines (structured, not chaotic web)
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=BLUE_PALE, width=3)
    return img


def flow_nodes(seed):
    img, d, rnd = base_canvas(seed)
    # orchestration flow: rounded rects connected left to right (agent pipeline)
    n = 5
    y = H // 2
    xs = [int(W * (i + 1) / (n + 1)) for i in range(n)]
    for i, x in enumerate(xs):
        w_, h_ = 220, 130
        col = BLUE if i in (0, n - 1) else WHITE
        outline = BLUE if i not in (0, n - 1) else BLUE
        d.rounded_rectangle([x - w_ / 2, y - h_ / 2, x + w_ / 2, y + h_ / 2],
                             radius=18, fill=col, outline=outline, width=4)
        if i < n - 1:
            d.line([(x + w_ / 2, y), (xs[i + 1] - w_ / 2, y)], fill=MUTE, width=3)
            ax = xs[i + 1] - w_ / 2
            d.polygon([(ax - 16, y - 10), (ax, y), (ax - 16, y + 10)], fill=MUTE)
    return img


def code_lines(seed):
    img, d, rnd = base_canvas(seed)
    # editor / terminal feel: a soft window with staggered "code" lines
    pad = 260
    d.rounded_rectangle([pad, 220, W - pad, H - 220], radius=28, fill=WHITE, outline=FAINT, width=3)
    d.rounded_rectangle([pad, 220, W - pad, 320], radius=28, fill=BLUE_PALE)
    for i, cx in enumerate([pad + 60, pad + 110, pad + 160]):
        d.ellipse([cx, 255, cx + 30, 285], fill=BLUE if i == 0 else MUTE)
    ly = 380
    widths = [0.75, 0.4, 0.6, 0.3, 0.68, 0.5, 0.35, 0.72, 0.45]
    for i, wr in enumerate(widths):
        indent = pad + 70 + (40 if i in (2, 3, 6) else 0)
        lw = int((W - 2 * pad - 140) * wr)
        color = BLUE if i % 4 == 0 else INK if i % 3 else MUTE
        d.rounded_rectangle([indent, ly, indent + lw, ly + 26], radius=13, fill=color)
        ly += 60
    return img


def dash_panels(seed):
    img, d, rnd = base_canvas(seed)
    margin = 220
    cols, rows = 2, 2
    gap = 40
    cw = (W - 2 * margin - gap) / cols
    ch = (H - 2 * margin - gap) / rows
    k = 0
    for r in range(rows):
        for c in range(cols):
            x0 = margin + c * (cw + gap)
            y0 = margin + r * (ch + gap)
            d.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], radius=22, fill=WHITE, outline=FAINT, width=3)
            if k == 0:
                bar_w = cw * 0.7
                d.rounded_rectangle([x0 + 40, y0 + ch - 60, x0 + 40 + bar_w, y0 + ch - 30], radius=10, fill=BLUE_PALE)
                d.rounded_rectangle([x0 + 40, y0 + ch - 60, x0 + 40 + bar_w * 0.62, y0 + ch - 30], radius=10, fill=BLUE)
            else:
                pts = []
                for i in range(6):
                    px = x0 + 40 + i * (cw - 80) / 5
                    py = y0 + ch / 2 + math.sin(i * 1.3 + k) * ch * 0.18
                    pts.append((px, py))
                d.line(pts, fill=BLUE, width=6, joint="curve")
            k += 1
    return img


def server_rows(seed):
    img, d, rnd = base_canvas(seed)
    margin = 260
    rows = 6
    rh = (H - 2 * margin) / rows - 14
    for i in range(rows):
        y0 = margin + i * (rh + 14)
        d.rounded_rectangle([margin, y0, W - margin, y0 + rh], radius=10, fill=WHITE, outline=FAINT, width=3)
        for j in range(3):
            lx = margin + 40 + j * 26
            lit = (i + j) % 5 == 0
            d.ellipse([lx, y0 + rh / 2 - 8, lx + 16, y0 + rh / 2 + 8], fill=BLUE if lit else FAINT)
    return img


def chip_grid(seed):
    img, d, rnd = base_canvas(seed)
    cx, cy = W / 2, H / 2
    size = 620
    d.rounded_rectangle([cx - size / 2, cy - size / 2, cx + size / 2, cy + size / 2],
                         radius=24, fill=WHITE, outline=BLUE, width=5)
    inner = size * 0.62
    gx = 6
    cell = inner / gx
    for i in range(gx):
        for j in range(gx):
            x0 = cx - inner / 2 + i * cell
            y0 = cy - inner / 2 + j * cell
            shade = BLUE_PALE if (i + j) % 2 == 0 else FAINT
            d.rectangle([x0 + 3, y0 + 3, x0 + cell - 3, y0 + cell - 3], fill=shade)
    # pins
    pin_len = 70
    n_pins = 8
    for i in range(n_pins):
        t = (i + 0.5) / n_pins
        px = cx - size / 2 + t * size
        d.line([(px, cy - size / 2), (px, cy - size / 2 - pin_len)], fill=MUTE, width=6)
        d.line([(px, cy + size / 2), (px, cy + size / 2 + pin_len)], fill=MUTE, width=6)
    return img


def arm_silhouette(seed):
    img, d, rnd = base_canvas(seed)
    base_x, base_y = W * 0.32, H * 0.85
    d.rectangle([base_x - 130, base_y, base_x + 130, base_y + 60], fill=INK)
    j1 = (base_x, base_y - 420)
    j2 = (base_x + 420, base_y - 560)
    j3 = (base_x + 760, base_y - 320)
    d.line([(base_x, base_y), j1], fill=INK, width=48, joint="curve")
    d.line([j1, j2], fill=BLUE, width=40, joint="curve")
    d.line([j2, j3], fill=INK, width=34, joint="curve")
    for p, r in [(j1, 34), (j2, 30), (j3, 26)]:
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=WHITE, outline=BLUE, width=8)
    d.polygon([(j3[0], j3[1] - 20), (j3[0] + 60, j3[1] + 10), (j3[0], j3[1] + 40)], fill=MUTE)
    return img


def pulse_line(seed):
    img, d, rnd = base_canvas(seed)
    y = H / 2
    pts = []
    x = 200
    while x < W - 200:
        pts.append((x, y))
        x += 40
        pts.append((x, y - 30))
        x += 30
        pts.append((x, y + 220))
        x += 20
        pts.append((x, y - 260))
        x += 20
        pts.append((x, y))
        x += 60
    d.line(pts, fill=BLUE, width=8, joint="curve")
    d.ellipse([W / 2 - 14, y - 14, W / 2 + 14, y + 14], fill=BLUE_DEEP)
    d.arc([W / 2 - 220, y - 220, W / 2 + 220, y + 220], 200, 340, fill=FAINT, width=4)
    return img


def shield_grid(seed):
    img, d, rnd = base_canvas(seed)
    cx, cy = W / 2, H / 2
    w_, h_ = 520, 640
    pts = [(cx - w_ / 2, cy - h_ / 2), (cx + w_ / 2, cy - h_ / 2),
           (cx + w_ / 2, cy + h_ * 0.05), (cx, cy + h_ / 2), (cx - w_ / 2, cy + h_ * 0.05)]
    d.polygon(pts, fill=WHITE, outline=BLUE, width=6)
    step = 46
    for yy in range(int(cy - h_ / 2) + 30, int(cy + h_ / 2) - 20, step):
        d.line([(cx - w_ / 2 + 30, yy), (cx + w_ / 2 - 30, yy)], fill=BLUE_PALE, width=4)
    d.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=BLUE)
    return img


def contour_waves(seed):
    img, d, rnd = base_canvas(seed)
    for k in range(7):
        pts = []
        amp = 60 + k * 14
        yoff = 260 + k * 150
        for x in range(0, W + 20, 20):
            yv = yoff + amp * math.sin(x / 260 + k)
            pts.append((x, yv))
        d.line(pts, fill=BLUE if k % 3 == 0 else FAINT, width=5 if k % 3 == 0 else 3, joint="curve")
    return img


def brush_strokes(seed):
    img, d, rnd = base_canvas(seed)
    for i in range(5):
        x0 = 200 + i * 420
        d.rounded_rectangle([x0, 260, x0 + 240, H - 260], radius=120,
                             fill=BLUE if i % 2 == 0 else BLUE_PALE)
    return img


def bar_ascend(seed):
    img, d, rnd = base_canvas(seed)
    n = 7
    margin = 260
    base_y = H - margin
    bw = (W - 2 * margin) / (n * 1.6)
    for i in range(n):
        hgt = (i + 1) / n * (H - 2 * margin) * 0.85
        x0 = margin + i * bw * 1.6
        d.rounded_rectangle([x0, base_y - hgt, x0 + bw, base_y], radius=8,
                             fill=BLUE if i == n - 1 else BLUE_PALE)
    d.line([(margin, base_y), (W - margin, base_y)], fill=INK, width=4)
    return img


def waveform(seed):
    img, d, rnd = base_canvas(seed)
    rnd2 = random.Random(seed)
    n = 46
    margin = 260
    bw = (W - 2 * margin) / n
    for i in range(n):
        hgt = (0.2 + 0.8 * abs(math.sin(i * 0.4 + seed))) * (H - 2 * margin) * 0.6
        x0 = margin + i * bw
        d.rounded_rectangle([x0, H / 2 - hgt / 2, x0 + bw * 0.6, H / 2 + hgt / 2],
                             radius=6, fill=BLUE if i % 5 == 0 else BLUE_PALE)
    return img


def layered_frames(seed):
    img, d, rnd = base_canvas(seed)
    cx, cy = W / 2, H / 2
    for i, off in enumerate([120, 60, 0]):
        w_, h_ = 900 - off, 560 - off * 0.6
        col = BLUE if i == 2 else FAINT
        d.rounded_rectangle([cx - w_ / 2 + off * 0.3, cy - h_ / 2 - off * 0.2,
                              cx + w_ / 2 + off * 0.3, cy + h_ / 2 - off * 0.2],
                             radius=20, outline=col, width=6, fill=WHITE if i == 2 else None)
    return img


def balance_scale(seed):
    img, d, rnd = base_canvas(seed)
    cx, cy = W / 2, H * 0.42
    d.line([(cx, cy), (cx, H - 300)], fill=INK, width=14)
    d.line([(cx - 500, cy), (cx + 500, cy)], fill=INK, width=10)
    for dx in (-500, 500):
        px = cx + dx
        d.line([(px, cy), (px - 90, cy + 160)], fill=MUTE, width=4)
        d.line([(px, cy), (px + 90, cy + 160)], fill=MUTE, width=4)
        d.arc([px - 110, cy + 100, px + 110, cy + 260], 0, 180, fill=BLUE, width=10)
    d.rectangle([cx - 220, H - 300, cx + 220, H - 260], fill=INK)
    return img


BUILDERS = {
    "lab_grid": lab_grid, "flow_nodes": flow_nodes, "code_lines": code_lines,
    "dash_panels": dash_panels, "server_rows": server_rows, "chip_grid": chip_grid,
    "arm_silhouette": arm_silhouette, "pulse_line": pulse_line, "shield_grid": shield_grid,
    "contour_waves": contour_waves, "brush_strokes": brush_strokes, "bar_ascend": bar_ascend,
    "waveform": waveform, "layered_frames": layered_frames, "balance_scale": balance_scale,
}

VARIANTS_PER_CATEGORY = 6  # -> 15 categories x 6 = 90 local placeholders (+ cover/dividers)


def soften(img):
    return img.filter(ImageFilter.SMOOTH_MORE)


def generate(root: Path):
    global W, H
    manifest = []
    for cat, style in CATEGORY_STYLES.items():
        cat_dir = root / "assets" / "stock" / cat
        cat_dir.mkdir(parents=True, exist_ok=True)
        fn = BUILDERS[style]
        for v in range(VARIANTS_PER_CATEGORY):
            seed = hash((cat, v)) % 10000
            img = soften(fn(seed))
            name = f"{cat}_{v+1:02d}.png"
            path = cat_dir / name
            img.save(path, quality=92)
            manifest.append({
                "file": str(path.relative_to(root)),
                "category": cat,
                "style": style,
                "width": W, "height": H, "orientation": "landscape",
                "source": "local_placeholder_v1",
            })
    # cover + section divider heroes: rendered full-bleed at the ACTUAL portrait
    # aspect ratio they're embedded at, using only styles that fill edge-to-edge
    # (no centered-composition styles here, or a portrait crop shows mostly
    # blank canvas — that was a real bug caught in visual QA).
    covers_dir = root / "assets" / "stock" / "_covers"
    covers_dir.mkdir(parents=True, exist_ok=True)
    orig_w, orig_h = W, H
    hero_specs = [
        ("cover_hero", "lab_grid", 999, 1544, 1800),
        ("divider_generative_ai", "chip_grid", 21, 1375, 1800),
        ("divider_developer_ai", "server_rows", 22, 1375, 1800),
        ("divider_infrastructure", "server_rows", 23, 1375, 1800),
        ("divider_robotics", "contour_waves", 24, 1375, 1800),
        ("divider_governance", "bar_ascend", 25, 1375, 1800),
    ]
    for name, fn_name, seed, w, h in hero_specs:
        W, H = w, h
        img = soften(BUILDERS[fn_name](seed))
        path = covers_dir / f"{name}.png"
        img.save(path)
        manifest.append({"file": str(path.relative_to(root)), "category": "_covers",
                          "style": fn_name, "width": w, "height": h,
                          "source": "local_placeholder_v1"})
    W, H = orig_w, orig_h
    return manifest


if __name__ == "__main__":
    import json
    root = Path(__file__).resolve().parents[1]
    manifest = generate(root)
    out = root / "assets" / "manifest" / "image_manifest.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2))
    print(f"Generated {len(manifest)} images -> {out}")
