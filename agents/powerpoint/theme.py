"""
theme.py

Centralized design system for the Enterprise AI Intelligence Report.

Every color, font, spacing value, and styling constant used across the
presentation is defined here.

Changing the theme should never require editing slide logic.
"""

from dataclasses import dataclass
from pptx.dml.color import RGBColor
from pptx.util import Pt, Inches


# ============================================================
# COLORS
# ============================================================

@dataclass(frozen=True)
class Colors:
    PRIMARY = RGBColor(15, 38, 71)          # Royal Navy
    SECONDARY = RGBColor(32, 82, 149)       # Executive Blue
    ACCENT = RGBColor(242, 169, 0)          # Luxury Gold

    SUCCESS = RGBColor(34, 139, 34)
    WARNING = RGBColor(255, 140, 0)
    DANGER = RGBColor(200, 40, 40)

    WHITE = RGBColor(255, 255, 255)

    BACKGROUND = RGBColor(248, 249, 252)

    CARD = RGBColor(255, 255, 255)

    BORDER = RGBColor(223, 227, 235)

    LIGHT_TEXT = RGBColor(110, 120, 140)

    TEXT = RGBColor(35, 35, 35)

    FOOTER = RGBColor(150, 150, 150)


# ============================================================
# TYPOGRAPHY
# ============================================================

@dataclass(frozen=True)
class Fonts:
    TITLE = "Aptos Display"
    HEADING = "Aptos Display"
    BODY = "Aptos"
    CAPTION = "Aptos"


@dataclass(frozen=True)
class FontSize:
    COVER_TITLE = Pt(30)
    COVER_SUBTITLE = Pt(18)

    TITLE = Pt(24)

    SECTION = Pt(18)

    BODY = Pt(14)

    SMALL = Pt(11)

    FOOTER = Pt(9)


# ============================================================
# SPACING
# ============================================================

@dataclass(frozen=True)
class Spacing:
    PAGE_MARGIN = Inches(0.45)

    CARD_PADDING = Inches(0.18)

    CARD_GAP = Inches(0.18)

    SECTION_GAP = Inches(0.22)

    HEADER_HEIGHT = Inches(0.55)

    FOOTER_HEIGHT = Inches(0.30)


# ============================================================
# CARD STYLE
# ============================================================

@dataclass(frozen=True)
class CardStyle:
    BORDER_WIDTH = 1

    RADIUS = 0.08

    SHADOW_OFFSET = 0.02


# ============================================================
# SLIDE
# ============================================================

@dataclass(frozen=True)
class Slide:
    WIDTH = Inches(13.333)
    HEIGHT = Inches(7.5)