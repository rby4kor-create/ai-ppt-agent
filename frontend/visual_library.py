import json
import os

import streamlit as st

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST_PATH = os.path.join(ROOT_DIR, "assets", "manifest", "image_manifest.json")


def _load_images():
    if not os.path.exists(MANIFEST_PATH):
        return []
    try:
        with open(MANIFEST_PATH) as f:
            return json.load(f).get("images", [])
    except Exception:
        return []


def visual_library_page():
    st.markdown('<div class="section-title">Visual Library</div>', unsafe_allow_html=True)
    st.caption(
        "The local, curated image library topic slides are automatically selected from. "
        "Built by `python tools/download_images.py` from config/visual_taxonomy.json."
    )

    images = _load_images()

    if not images:
        st.warning(
            "The library is empty. Add a `PEXELS_API_KEY` (and/or `UNSPLASH_ACCESS_KEY`) "
            "to your `.env`, then run:\n\n"
            "```bash\npython tools/download_images.py\npython tools/deduplicate_images.py --apply\npython tools/validate_images.py\n```\n\n"
            "Generation still works without this - topic slides fall back to a live single-photo "
            "fetch or the bundled local category illustrations."
        )
        return

    categories = sorted(set(img.get("category", "uncategorized") for img in images))
    providers = sorted(set(img.get("provider", "unknown") for img in images))

    col1, col2, col3 = st.columns([2, 2, 3])
    with col1:
        category_filter = st.multiselect("Category", categories, default=[])
    with col2:
        provider_filter = st.multiselect("Provider", providers, default=[])
    with col3:
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
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total images", total)
    m2.metric("Categories", len(categories))
    m3.metric("Avg. quality score", avg_quality)
    m4.metric("Shown", len(filtered))

    st.divider()

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
                st.caption(
                    f"**{img.get('category', '?')}**  \n"
                    f"q={img.get('quality_score', '?')} · {img.get('provider', '?')}  \n"
                    f"{img.get('width', '?')}×{img.get('height', '?')}"
                )
                if img.get("photographer"):
                    st.caption(f"Photo: {img['photographer']}")
