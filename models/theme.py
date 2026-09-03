from pptx.dml.color import RGBColor
from pptx.util import Pt


class Theme:
    """
    Design system for the report, with two selectable premium palettes:

      - "Bosch Corporate": white/light backgrounds, near-black type,
        Bosch Red used sparingly as a single sharp accent.
      - "Modern Executive": dark navy backgrounds, warm gold accent,
        the "premium/stock-photo" look requested for the leadership
        deck - large image real estate, high-contrast white type,
        gold rules/labels instead of red.

    Every color/font call in powerpoint_agent.py reads from these class
    attributes, so switching the active palette (Theme.apply(name)) before
    a build changes the whole deck with no per-slide code changes.
    """

    NAMES = ["Bosch Corporate", "Modern Executive"]
    DEFAULT = "Bosch Corporate"

    _PALETTES = {
        "Bosch Corporate": dict(
            PRIMARY=RGBColor(0xE2, 0x00, 0x15),
            PRIMARY_DARK=RGBColor(0xBF, 0x00, 0x11),
            TEXT=RGBColor(0x11, 0x11, 0x11),
            SECONDARY_TEXT=RGBColor(0x55, 0x55, 0x55),
            MUTED=RGBColor(0x8A, 0x8A, 0x8A),
            WHITE=RGBColor(0xFF, 0xFF, 0xFF),
            BACKGROUND=RGBColor(0xFF, 0xFF, 0xFF),
            SOFT_BG=RGBColor(0xF7, 0xF7, 0xF7),
            BORDER=RGBColor(0xE5, 0xE5, 0xE5),
            DARK=RGBColor(0x15, 0x15, 0x15),
            PRIMARY_LIGHT=RGBColor(0xFC, 0xE7, 0xE9),
            HEADING_ON_DARK=RGBColor(0xFF, 0xFF, 0xFF),
            RISK_LOW=RGBColor(0x2E, 0x7D, 0x5B),
            RISK_MEDIUM=RGBColor(0xC8, 0x8A, 0x1E),
            RISK_HIGH=RGBColor(0xB5, 0x3D, 0x3D),
            FONT="Arial",
            FONT_HEADER="Arial",
        ),
        "Modern Executive": dict(
            # Warm gold accent on deep navy - the "premium/leadership deck"
            # look: dark cover + section panels, gold rules/labels/numerals,
            # white/near-white body type, generous full-bleed photography.
            PRIMARY=RGBColor(0xC9, 0xA2, 0x27),          # muted gold
            PRIMARY_DARK=RGBColor(0xA3, 0x82, 0x1B),
            TEXT=RGBColor(0xF5, 0xF6, 0xF8),              # near-white on dark panels
            SECONDARY_TEXT=RGBColor(0xB9, 0xC0, 0xCC),
            MUTED=RGBColor(0x8B, 0x93, 0xA1),
            WHITE=RGBColor(0xFF, 0xFF, 0xFF),
            BACKGROUND=RGBColor(0x0D, 0x14, 0x22),        # deep navy page bg
            SOFT_BG=RGBColor(0x16, 0x1F, 0x30),           # card/panel bg on navy
            BORDER=RGBColor(0x2A, 0x35, 0x49),
            DARK=RGBColor(0x0D, 0x14, 0x22),
            PRIMARY_LIGHT=RGBColor(0x3A, 0x33, 0x1A),
            HEADING_ON_DARK=RGBColor(0xFF, 0xFF, 0xFF),
            RISK_LOW=RGBColor(0x4C, 0xB3, 0x82),
            RISK_MEDIUM=RGBColor(0xE0, 0xA9, 0x3E),
            RISK_HIGH=RGBColor(0xE0, 0x6A, 0x6A),
            FONT="Arial",
            FONT_HEADER="Arial",
        ),
    }

    TITLE = Pt(30)
    SUBTITLE = Pt(18)
    BODY = Pt(14)
    SMALL = Pt(11)
    HEADER = Pt(13)
    STAT = Pt(40)

    @classmethod
    def apply(cls, name):
        """Sets the active palette. Falls back to DEFAULT for an unknown
        name instead of raising, since this is driven by a UI dropdown
        value that should never hard-crash a generation run."""
        palette = cls._PALETTES.get(name, cls._PALETTES[cls.DEFAULT])
        for key, value in palette.items():
            setattr(cls, key, value)
        cls.ACTIVE = name if name in cls._PALETTES else cls.DEFAULT
        # Back-compat aliases used elsewhere in the codebase.
        cls.BLACK = cls.TEXT
        cls.DARK_GRAY = cls.SECONDARY_TEXT
        cls.LIGHT_GRAY = cls.SOFT_BG
        cls.ACCENT = cls.PRIMARY
        cls.SECONDARY = cls.SECONDARY_TEXT
        return cls

    @classmethod
    def is_dark(cls):
        return getattr(cls, "ACTIVE", cls.DEFAULT) == "Modern Executive"


# Initialize with the default palette so `Theme.PRIMARY` etc. work for any
# code path that imports Theme without explicitly calling apply() first.
Theme.apply(Theme.DEFAULT)
