"""
layout.py

Centralized layout engine.

Every slide should derive its positioning from this file.
No slide should hardcode Inches(...) values.
"""

from dataclasses import dataclass
from pptx.util import Inches


@dataclass(frozen=True)
class Page:

    WIDTH = Inches(13.333)
    HEIGHT = Inches(7.5)

    LEFT = Inches(0.45)
    RIGHT = Inches(12.88)

    TOP = Inches(0.35)
    BOTTOM = Inches(7.15)


@dataclass(frozen=True)
class Header:

    X = Page.LEFT

    Y = Inches(0.20)

    WIDTH = Inches(12.40)

    HEIGHT = Inches(0.55)


@dataclass(frozen=True)
class Footer:

    X = Page.LEFT

    Y = Inches(7.05)

    WIDTH = Inches(12.40)

    HEIGHT = Inches(0.25)


@dataclass(frozen=True)
class Content:

    X = Page.LEFT

    Y = Inches(0.90)

    WIDTH = Inches(12.40)

    HEIGHT = Inches(5.90)


@dataclass(frozen=True)
class Grid:

    GAP = Inches(0.25)

    LEFT_WIDTH = Inches(7.70)

    RIGHT_WIDTH = Inches(4.45)

    LEFT_X = Content.X

    RIGHT_X = LEFT_X + LEFT_WIDTH + GAP

    TOP = Content.Y


@dataclass(frozen=True)
class Cards:

    SMALL_HEIGHT = Inches(1.10)

    MEDIUM_HEIGHT = Inches(1.80)

    LARGE_HEIGHT = Inches(2.80)

    IMAGE_HEIGHT = Inches(2.60)