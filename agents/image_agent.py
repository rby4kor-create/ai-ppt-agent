import hashlib
import json
import os

import requests
from PIL import Image

from utils.logger import get_logger

logger = get_logger(__name__)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets", "images")
STOCK_CACHE_DIR = os.path.join(ASSETS_DIR, "stock_cache")
LIBRARY_DIR = os.path.join(ROOT_DIR, "assets", "stock")
MANIFEST_PATH = os.path.join(ROOT_DIR, "assets", "manifest", "image_manifest.json")
TAXONOMY_PATH = os.path.join(ROOT_DIR, "config", "visual_taxonomy.json")

# Bridges the report's existing category names (used throughout
# presentation_builder.py / config_panel.py) to the 15 visual-taxonomy
# keys the 200-image library is organized under (config/visual_taxonomy.json).
# A category not listed here (or not yet in the library) falls back to
# "frontier_ai" as a safe default rather than crashing.
CATEGORY_TO_TAXONOMY = {
    "Large Language Models": "frontier_ai",
    "AI Agents": "agentic_ai",
    "Cloud AI": "infrastructure",
    "AI Hardware": "hardware",
    "AI Infrastructure": "infrastructure",
    "Robotics": "robotics",
    "Cybersecurity": "cybersecurity",
    "Healthcare AI": "healthcare",
    "Computer Vision": "multimodal",
    "Speech AI": "speech",
    "Developer AI": "developer_ai",
    "Generative AI": "creative_ai",
    "Enterprise AI": "enterprise_ai",
    "Enterprise Data": "enterprise_data",
    "AI Economics": "economics",
    "AI Governance": "governance",
    "General AI": "frontier_ai",
}

# Maps a category name to its static fallback asset (without extension)
# AND to the search query used against the stock-photo API. Categories
# not listed fall back to "general_ai". This is the LAST-RESORT path,
# used only when the curated 200-image library (assets/stock/, selected
# via `select_image_for_topic` below) has nothing usable for the category.
CATEGORY_ASSET = {
    "Large Language Models": "large_language_models",
    "AI Agents": "ai_agents",
    "Cloud AI": "cloud_ai",
    "AI Hardware": "ai_hardware",
    "AI Infrastructure": "ai_infrastructure",
    "Robotics": "robotics",
    "Cybersecurity": "cybersecurity",
    "Healthcare AI": "healthcare_ai",
    "Computer Vision": "computer_vision",
    "Speech AI": "speech_ai",
    "Developer AI": "developer_ai",
    "Generative AI": "generative_ai",
    "General AI": "general_ai",
}

CATEGORY_STOCK_QUERY = {
    "Large Language Models": "artificial intelligence neural network abstract",
    "AI Agents": "robotic automation technology office",
    "Cloud AI": "cloud computing data center servers",
    "AI Hardware": "computer processor chip technology",
    "AI Infrastructure": "data center server racks technology",
    "Robotics": "industrial robot arm automation",
    "Cybersecurity": "cybersecurity network security abstract",
    "Healthcare AI": "healthcare technology medical digital",
    "Computer Vision": "camera lens technology digital",
    "Speech AI": "microphone audio sound waves technology",
    "Developer AI": "software developer coding screen",
    "Generative AI": "generative art digital abstract technology",
    "General AI": "artificial intelligence technology abstract",
}
DEFAULT_STOCK_QUERY = "technology business abstract"
COVER_STOCK_QUERY = "modern office skyline technology"


class ImageAgent:
    """
    Resolves the image to show on a topic/section/cover slide.

    Resolution order per topic:
      1. article.image_path, if the article actually has one.
      2. The curated 200-image local library (assets/stock/<category>/,
         built by tools/download_images.py from config/visual_taxonomy.json
         and indexed in assets/manifest/image_manifest.json) - see
         `select_image_for_topic`. This is fully offline once populated:
         no network call happens on a normal weekly generation run.
      3. A live single-photo Unsplash fetch by category query, cached to
         disk (assets/images/stock_cache/) - kept as a fallback for
         categories the curated library doesn't cover yet.
      4. category-specific static local asset (assets/images/<category>.png).
      5. general_ai.png as the last-resort fallback.

    "Image Not Available" placeholders are never shown, since a category
    asset always exists as the final fallback.
    """

    UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"

    def __init__(self):
        self.access_key = os.getenv("UNSPLASH_ACCESS_KEY", "").strip()
        os.makedirs(STOCK_CACHE_DIR, exist_ok=True)
        self._manifest_by_category = None  # lazy-loaded, see _load_manifest()
        self._taxonomy = None
        self._used_ids = set()  # images already placed in THIS deck - avoid repeats

    def reset_usage(self):
        """Call once per PPT generation run so image reuse is tracked
        per-deck, not across the process's whole lifetime."""
        self._used_ids = set()

    # ------------------------------------------------------------------
    # Curated library (manifest-driven, layout-aware selection)
    # ------------------------------------------------------------------

    def _load_manifest(self):
        if self._manifest_by_category is not None:
            return
        self._manifest_by_category = {}
        if os.path.exists(MANIFEST_PATH):
            try:
                with open(MANIFEST_PATH) as f:
                    manifest = json.load(f)
                for img in manifest.get("images", []):
                    self._manifest_by_category.setdefault(img["category"], []).append(img)
            except Exception as e:
                logger.warning(f"Could not read image manifest: {e}")
        if self._taxonomy is None:
            self._taxonomy = {}
            if os.path.exists(TAXONOMY_PATH):
                try:
                    with open(TAXONOMY_PATH) as f:
                        self._taxonomy = json.load(f)
                except Exception as e:
                    logger.warning(f"Could not read visual taxonomy: {e}")

    def _score_candidate(self, img, keywords, target_aspect):
        """
        Ranks a manifest image against a topic per the weighted scheme:
          semantic relevance 35%, category match 20% (implicit - the
          candidate pool is already filtered to the resolved category),
          composition 15%, editorial quality 10%, resolution 10%,
          slide-layout compatibility 10%.
        """
        tags = set(t.lower() for t in img.get("tags", []))
        text_blob = " ".join([img.get("id", ""), *tags]).lower()
        relevance = sum(1 for kw in keywords if kw.lower() in text_blob)
        relevance_score = min(1.0, relevance / max(1, len(keywords))) if keywords else 0.5

        category_match = 1.0  # pool is pre-filtered to the target category

        # Composition proxy: real per-image composition/text-safe tags
        # aren't populated without a vision pass, so this uses the
        # image's own aspect ratio as the best available signal - an
        # aspect close to the target slide box crops with less loss.
        img_aspect = img.get("aspect_ratio") or (img.get("width", 1) / max(1, img.get("height", 1)))
        aspect_diff = abs(img_aspect - target_aspect)
        composition_score = max(0.0, 1.0 - aspect_diff / target_aspect)

        editorial_score = img.get("quality_score", 0.8)
        resolution_score = min(1.0, max(img.get("width", 0), img.get("height", 0)) / 2400)
        layout_score = composition_score  # same proxy; kept as a separate term per the spec's weighting

        # Mild penalty (not exclusion) for an image already used elsewhere
        # in this deck, so a strong match can still be reused rather than
        # forcing a visually worse "different" image, but a fresh image
        # wins any close call.
        reuse_penalty = 0.15 if img["id"] in self._used_ids else 0.0

        score = (
            relevance_score * 0.35
            + category_match * 0.20
            + composition_score * 0.15
            + editorial_score * 0.10
            + resolution_score * 0.10
            + layout_score * 0.10
            - reuse_penalty
        )
        return score

    def select_top_candidates(self, category, title="", keywords=None, layout="text_left_image_right", n=3):
        """
        Non-mutating "peek" version of select_image_for_topic: returns up
        to `n` (path, score, image_id) candidates ranked the same way,
        WITHOUT marking any of them as used. Powers the frontend's
        Story -> Recommended visual / Alternative 1 / Alternative 2
        preview (spec section 32) so a person can override the
        auto-selection without it affecting what generation actually picks.
        """
        self._load_manifest()
        taxonomy_key = CATEGORY_TO_TAXONOMY.get(category, "frontier_ai")
        candidates = self._manifest_by_category.get(taxonomy_key, [])
        if not candidates:
            return []

        kw = set(k.lower() for k in (keywords or []))
        for word in (title or "").lower().split():
            if len(word) > 3:
                kw.add(word)
        taxonomy_kw = self._taxonomy.get(taxonomy_key, {}).get("keywords", [])
        kw.update(k.lower() for k in taxonomy_kw)

        target_aspect = {
            "text_left_image_right": 1.3,
            "full_bleed_right": 0.9,
            "full_bleed": 1.5,
        }.get(layout, 1.3)

        ranked = sorted(candidates, key=lambda img: self._score_candidate(img, kw, target_aspect), reverse=True)
        results = []
        for img in ranked[:n]:
            path = os.path.join(ROOT_DIR, img["relative_path"])
            if os.path.exists(path):
                score = self._score_candidate(img, kw, target_aspect)
                results.append({"path": path, "score": round(min(1.0, max(0.0, score)), 3), "id": img["id"]})
        return results

    def select_image_for_topic(self, category, title="", keywords=None, layout="text_left_image_right"):
        """
        Semantic, layout-aware selection from the curated local library.
        Returns an absolute file path, or "" if the library has nothing
        for this category yet (caller should fall through to the live
        fetch / static asset).
        """
        self._load_manifest()
        taxonomy_key = CATEGORY_TO_TAXONOMY.get(category, "frontier_ai")
        candidates = self._manifest_by_category.get(taxonomy_key, [])
        if not candidates:
            return ""

        kw = set(k.lower() for k in (keywords or []))
        for word in (title or "").lower().split():
            if len(word) > 3:
                kw.add(word)
        taxonomy_kw = self._taxonomy.get(taxonomy_key, {}).get("keywords", [])
        kw.update(k.lower() for k in taxonomy_kw)

        # Widescreen right-hand image panel on a topic slide is roughly
        # square-ish to 16:10 depending on layout; full-bleed cover/section
        # panels are taller. Callers pass the intended box shape via
        # `layout` so the ranker can prefer a compatible source aspect
        # rather than always assuming one shape.
        target_aspect = {
            "text_left_image_right": 1.3,
            "full_bleed_right": 0.9,
            "full_bleed": 1.5,
        }.get(layout, 1.3)

        ranked = sorted(candidates, key=lambda img: self._score_candidate(img, kw, target_aspect), reverse=True)
        best = ranked[0]
        path = os.path.join(ROOT_DIR, best["relative_path"])
        if os.path.exists(path):
            self._used_ids.add(best["id"])
            return path
        return ""

    # ------------------------------------------------------------------
    # Live single-photo fetch (fallback for categories not yet in the
    # curated library)
    # ------------------------------------------------------------------

    def _stock_cache_path(self, query):
        key = hashlib.sha1(query.encode("utf-8")).hexdigest()[:16]
        return os.path.join(STOCK_CACHE_DIR, f"stock_{key}.jpg")

    def _fetch_stock_photo(self, query):
        """
        Returns a local file path to a real downloaded stock photo for
        `query`, or "" if no API key is configured, the request fails,
        or there's no network access. Never raises - a missing/failed
        stock photo always falls through to the local static asset so
        generation is never blocked on external network availability.
        """
        if not self.access_key:
            return ""

        cache_path = self._stock_cache_path(query)
        if os.path.exists(cache_path):
            return cache_path

        try:
            resp = requests.get(
                self.UNSPLASH_SEARCH_URL,
                params={"query": query, "per_page": 1, "orientation": "landscape"},
                headers={"Authorization": f"Client-ID {self.access_key}"},
                timeout=8,
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
            if not results:
                logger.info(f"No Unsplash results for query: {query!r}")
                return ""

            image_url = results[0]["urls"]["regular"]
            img_resp = requests.get(image_url, timeout=15)
            img_resp.raise_for_status()

            with open(cache_path, "wb") as f:
                f.write(img_resp.content)
            logger.info(f"Downloaded stock photo for query: {query!r}")
            return cache_path

        except Exception as e:
            logger.warning(f"Stock photo fetch failed for query {query!r}: {e}")
            return ""

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def resolve_image_path(self, category, article_image_path="", title="", keywords=None, layout="text_left_image_right"):
        if article_image_path and os.path.exists(article_image_path):
            return article_image_path

        library_path = self.select_image_for_topic(category, title=title, keywords=keywords, layout=layout)
        if library_path:
            return library_path

        query = CATEGORY_STOCK_QUERY.get(category, DEFAULT_STOCK_QUERY)
        stock_path = self._fetch_stock_photo(query)
        if stock_path:
            return stock_path

        asset_key = CATEGORY_ASSET.get(category, "general_ai")
        path = os.path.join(ASSETS_DIR, f"{asset_key}.png")
        if os.path.exists(path):
            return path

        fallback = os.path.join(ASSETS_DIR, "general_ai.png")
        return fallback if os.path.exists(fallback) else ""

    def cover_asset_path(self):
        stock_path = self._fetch_stock_photo(COVER_STOCK_QUERY)
        if stock_path:
            return stock_path

        path = os.path.join(ASSETS_DIR, "cover_hero.png")
        return path if os.path.exists(path) else ""

    def add_cropped_image(self, slide, image_path, left, top, width, height):
        """
        Adds `image_path` into the exact bounding box (left, top, width,
        height), center-cropping the source so the box is filled with no
        distortion and no letterbox gaps - equivalent to CSS
        `object-fit: cover`.
        """
        if not image_path or not os.path.exists(image_path):
            return None

        box_ratio = width / height
        with Image.open(image_path) as im:
            src_w, src_h = im.size
        src_ratio = src_w / src_h

        if src_ratio > box_ratio:
            # source is relatively wider than the box -> crop left/right
            crop_frac = 1 - (box_ratio / src_ratio)
            crop_left = crop_frac / 2
            crop_right = crop_frac / 2
            crop_top = crop_bottom = 0.0
        else:
            # source is relatively taller than the box -> crop top/bottom
            crop_frac = 1 - (src_ratio / box_ratio)
            crop_top = crop_frac / 2
            crop_bottom = crop_frac / 2
            crop_left = crop_right = 0.0

        pic = slide.shapes.add_picture(image_path, left, top, width=width, height=height)
        pic.crop_left = crop_left
        pic.crop_right = crop_right
        pic.crop_top = crop_top
        pic.crop_bottom = crop_bottom
        pic.line.fill.background()
        pic.shadow.inherit = False
        return pic
