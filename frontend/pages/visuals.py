"""
Visuals -- editorial redesign of the visual library. Reads the same
manifest (assets/manifest/image_manifest.json) built by
tools/download_images.py; when it's empty, falls back to showing the
bundled category illustration assets that actually ship in assets/ so
the page never renders truly blank, and shows an honest instruction
for populating the full library instead of a raw warning.
"""
import json
import os

import streamlit as st

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST_PATH = os.path.join(ROOT_DIR, "assets", "manifest", "image_manifest.json")

FALLBACK_ILLUSTRATIONS = [
    ("ai_agents.png", "AI Agents"),
    ("ai_hardware.png", "AI Hardware"),
    ("ai_infrastructure.png", "AI Infrastructure"),
    ("cloud_ai.png", "Cloud AI"),
    ("computer_vision.png", "Computer Vision"),
    ("cybersecurity.png", "Cybersecurity"),
    ("developer_ai.png", "Developer AI"),
    ("general_ai.png", "General AI"),
    ("generative_ai.png", "Generative AI"),
    ("healthcare_ai.png", "Healthcare AI"),
    ("large_language_models.png", "Large Language Models"),
    ("robotics.png", "Robotics"),
    ("speech_ai.png", "Speech AI"),
]


def _load_manifest_images():
    if not os.path.exists(MANIFEST_PATH):
        return []
    try:
        with open(MANIFEST_PATH) as f:
            return json.load(f).get("images", [])
    except Exception:
        return []


def _render_manifest_grid(images):
    categories = sorted(set(img.get("category", "uncategorized") for img in images))
    providers = sorted(set(img.get("provider", "unknown") for img in images))

    c1, c2, c3 = st.columns([2, 2, 3])
    with c1:
        category_filter = st.multiselect("Category", categories, default=[])
    with c2:
        provider_filter = st.multiselect("Provider", providers, default=[])
    with c3:
        search = st.text_input("Search (id / tags)", "")

    filtered = images
    if category_filter:
        filtered = [i for i in filtered if i.get("category") in category_filter]
    if provider_filter:
        filtered = [i for i in filtered if i.get("provider") in provider_filter]
    if search.strip():
        needle = search.strip().lower()
        filtered = [
            i for i in filtered
            if needle in i.get("id", "").lower()
            or any(needle in t.lower() for t in i.get("tags", []))
            or needle in i.get("category", "").lower()
        ]

    total = len(images)
    avg_quality = round(sum(i.get("quality_score", 0) for i in images) / total, 3) if total else 0

    html = f"""
<div class="metric-strip">
    <div class="metric-cell"><div class="m-label">Total Images</div><div class="m-value">{total}</div></div>
    <div class="metric-cell"><div class="m-label">Categories</div><div class="m-value">{len(categories)}</div></div>
    <div class="metric-cell"><div class="m-label">Avg. Quality</div><div class="m-value">{avg_quality}</div></div>
    <div class="metric-cell"><div class="m-label">Shown</div><div class="m-value">{len(filtered)}</div></div>
</div>
""".strip()
    st.markdown(html, unsafe_allow_html=True)
    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)

    cols_per_row = 4
    for i in range(0, len(filtered), cols_per_row):
        row = filtered[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, img in zip(cols, row):
            path = os.path.join(ROOT_DIR, img.get("relative_path", ""))
            with col:
                if os.path.exists(path):
                    st.image(path, use_container_width=True)
                else:
                    st.caption("(file missing)")
                st.markdown(
                    f'<div class="vis-caption"><b>{img.get("category", "?")}</b><br>'
                    f'q={img.get("quality_score", "?")} &middot; {img.get("provider", "?")}<br>'
                    f'{img.get("width", "?")}&times;{img.get("height", "?")}</div>',
                    unsafe_allow_html=True,
                )
                if img.get("photographer"):
                    st.caption(f"Photo: {img['photographer']}")


def _render_fallback_grid():
    st.markdown(
        '<div class="empty-state" style="margin-bottom:28px;">'
        '<div class="empty-eyebrow">Full Library Not Yet Populated</div>'
        '<div class="empty-title">Showing the bundled category illustrations</div>'
        '<div class="empty-sub">Add a <code>PEXELS_API_KEY</code> or '
        '<code>UNSPLASH_ACCESS_KEY</code> to your <code>.env</code>, then run '
        '<code>python tools/download_images.py</code> to build the full curated library. '
        'Generation still works without this — topic slides fall back to these local '
        'illustrations or a live single-photo fetch.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    available = [(fname, label) for fname, label in FALLBACK_ILLUSTRATIONS if os.path.exists(os.path.join(ROOT_DIR, "assets", fname))]
    if not available:
        return

    cols_per_row = 4
    for i in range(0, len(available), cols_per_row):
        row = available[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, (fname, label) in zip(cols, row):
            with col:
                st.image(os.path.join(ROOT_DIR, "assets", fname), use_container_width=True)
                st.markdown(f'<div class="vis-caption"><b>{label}</b><br>Bundled illustration</div>', unsafe_allow_html=True)


def render():
    st.markdown(
        '<div class="section-head"><div class="section-title">Visual Library</div>'
        '<div class="section-note">The curated archive topic slides draw from</div></div>',
        unsafe_allow_html=True,
    )

    images = _load_manifest_images()
    if images:
        _render_manifest_grid(images)
    else:
        _render_fallback_grid()
