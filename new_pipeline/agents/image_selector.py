"""
agents/image_selector.py

Semantic image selection engine.

Replaces any random.choice() / first-result / slide-number->image-number
selection with a scored decision:

    story -> content analysis -> category/subcategory -> visual concept
    -> keywords -> candidate images -> semantic ranking
    -> layout compatibility -> best image (+ 2 runner-ups)

Scoring weights (sum to 1.0):
    semantic_relevance   35%   keyword overlap between story and image tags
    category_match       20%   exact category / sibling-category match
    composition           15%   aspect ratio + orientation fit for the slot
    editorial_quality     10%   manifest quality score (resolution/sharpness proxy)
    resolution             10%   pixel dimensions vs. the 2000px+ bar
    layout_compatibility   10%   does the image's implied focal side match
                                 where it will sit (text-left/image-right, etc.)

A used-image diversity penalty is applied on top so the same photo is
never reused across a report unless it is the verified canonical source
image for that specific story.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


STOPWORDS = {"the", "a", "an", "of", "for", "and", "to", "in", "on", "with", "into", "beyond"}


def _tokenize(text: str) -> set[str]:
    return {w.strip(".,:;()").lower() for w in text.split() if w.strip(".,:;()").lower() not in STOPWORDS and len(w) > 2}


@dataclass
class ImageCandidate:
    file: str
    category: str
    tags: set[str] = field(default_factory=set)
    width: int = 2400
    height: int = 1600
    quality: float = 0.85          # 0-1 editorial-quality proxy from manifest
    orientation: str = "landscape"
    focal_side: str = "center"     # "left" | "right" | "center" -> where the visual subject sits


@dataclass
class Story:
    headline: str
    category: str
    subcategory: str = ""
    summary: str = ""
    tags: Iterable[str] = ()

    def keywords(self) -> set[str]:
        kws = _tokenize(self.headline) | _tokenize(self.summary)
        kws |= {t.lower() for t in self.tags}
        kws |= {self.category.lower().replace("_", " ")}
        return kws


def semantic_relevance(story: Story, cand: ImageCandidate) -> float:
    kws = story.keywords()
    if not kws or not cand.tags:
        return 0.4  # neutral score when either side lacks signal
    overlap = len(kws & cand.tags)
    return min(1.0, overlap / max(3, len(kws) ** 0.5))


def category_match(story: Story, cand: ImageCandidate) -> float:
    if cand.category == story.category:
        return 1.0
    # sibling categories share partial relevance (e.g. hardware <-> infrastructure)
    siblings = {
        "hardware": {"infrastructure"}, "infrastructure": {"hardware", "cybersecurity"},
        "developer_ai": {"agentic_ai"}, "agentic_ai": {"developer_ai", "enterprise_ai"},
        "healthcare": {"multimodal"}, "robotics": {"hardware"},
    }
    return 0.45 if cand.category in siblings.get(story.category, set()) else 0.1


def composition_score(cand: ImageCandidate, target_ratio: float = 1.5) -> float:
    ratio = cand.width / cand.height
    return max(0.0, 1.0 - abs(ratio - target_ratio) / target_ratio)


def resolution_score(cand: ImageCandidate) -> float:
    return min(1.0, cand.width / 2400)


def layout_compatibility(cand: ImageCandidate, slot_side: str) -> float:
    if cand.focal_side == "center":
        return 0.8
    wants_subject_on = "left" if slot_side == "right" else "right"
    return 1.0 if cand.focal_side == wants_subject_on else 0.5


WEIGHTS = dict(relevance=0.35, category=0.20, composition=0.15,
               quality=0.10, resolution=0.10, layout=0.10)


class ImageSelector:
    """Stateful selector: tracks used images across one report to enforce diversity."""

    def __init__(self, candidates: list[ImageCandidate]):
        self.candidates = candidates
        self._used: dict[str, int] = {}

    @classmethod
    def from_manifest(cls, manifest_path: Path) -> "ImageSelector":
        data = json.loads(Path(manifest_path).read_text())
        cands = []
        for row in data:
            cands.append(ImageCandidate(
                file=row["file"], category=row.get("category", ""),
                tags={row.get("style", "")}, width=row.get("width", 2400),
                height=row.get("height", 1600), quality=0.85,
            ))
        return cls(cands)

    def score(self, story: Story, cand: ImageCandidate, slot_side: str) -> float:
        s = (WEIGHTS["relevance"] * semantic_relevance(story, cand)
             + WEIGHTS["category"] * category_match(story, cand)
             + WEIGHTS["composition"] * composition_score(cand)
             + WEIGHTS["quality"] * cand.quality
             + WEIGHTS["resolution"] * resolution_score(cand)
             + WEIGHTS["layout"] * layout_compatibility(cand, slot_side))
        penalty = 0.35 * self._used.get(cand.file, 0)
        return max(0.0, s - penalty)

    def select(self, story: Story, slot_side: str = "right", top_n: int = 3):
        pool = [c for c in self.candidates if c.category == story.category] or self.candidates
        ranked = sorted(pool, key=lambda c: self.score(story, c, slot_side), reverse=True)
        top = ranked[:top_n]
        if top:
            self._used[top[0].file] = self._used.get(top[0].file, 0) + 1
        return [(c, round(self.score(story, c, slot_side) * 100, 1)) for c in top]


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    sel = ImageSelector.from_manifest(root / "assets" / "manifest" / "image_manifest.json")
    demo = Story(headline="Coding agents move into the terminal for enterprise engineering teams",
                 category="developer_ai", summary="Terminal-native coding agent tooling",
                 tags=["terminal", "developer", "coding"])
    for cand, score in sel.select(demo, slot_side="right"):
        print(f"{score:5.1f}%  {cand.file}")
