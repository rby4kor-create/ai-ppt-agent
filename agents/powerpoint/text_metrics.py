"""
Real text-measurement helpers for the PowerPoint generator.

Why this exists
----------------
The previous layout code decided how many lines a piece of text would
wrap to using a crude character-count heuristic
(``chars_per_line = box_width / avg_char_width``). That estimate is
wrong often enough - proportional fonts don't have a fixed average
character width, and the error compounds every time one text block's
line count is fed into the next block's start position - that on real
content it produced visible bugs:

  * Weekly Signals: a headline the heuristic thought was "one line"
    actually wrapped to two, and the fixed row height didn't account
    for it, so the second line printed on top of the description.
  * Topic slides: a three-line title's real wrapped line count didn't
    match the estimate, so every block below it (bullets, Enterprise
    Intelligence, Recommendation, Source) drifted out of position and
    the Recommendation line ended up overlapping the Source line.

This module replaces the heuristic with pixel-accurate measurement
using Liberation Sans - the font LibreOffice/most Linux PowerPoint
viewers substitute for Arial, and metric-compatible with it - via
PIL's ImageFont. Word-wrapping is computed the same way a real text
box wraps: greedily add words to a line until the next word would
exceed the box width.

If the font files aren't available in a given environment, every
function degrades gracefully to the old character-count estimate
rather than raising, so a missing font package never breaks a build.
"""

import functools
import os

try:
    from PIL import ImageFont
    _PIL_AVAILABLE = True
except Exception:  # pragma: no cover - Pillow should always be present
    _PIL_AVAILABLE = False

_FONT_PATHS = {
    (False, False): [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ],
    (True, False): [
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ],
}

# Rendered at a large reference pixel size and scaled down for accuracy
# (small bitmap sizes round glyph widths to whole pixels, which distorts
# ratios between characters). 200px references a font size close to
# what we'll actually query, keeping hinting effects consistent.
_REF_PX = 200


@functools.lru_cache(maxsize=8)
def _load_font(bold):
    if not _PIL_AVAILABLE:
        return None
    for path in _FONT_PATHS.get((bold, False), []):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, _REF_PX)
            except Exception:
                continue
    return None


@functools.lru_cache(maxsize=4096)
def _char_widths_ratio(bold):
    """Returns (font_object_or_None,) - cached loader indirection so the
    real per-string measurement below has a single fast cache key."""
    return _load_font(bold)


def _measure_width_in(text, font_pt, bold=False):
    """
    Width of `text` in inches, set at `font_pt`. Falls back to the old
    0.52x-of-point-size heuristic if PIL/fonts are unavailable.
    """
    font = _load_font(bold)
    if font is None or not text:
        if not text:
            return 0.0
        return len(text) * (font_pt * 0.52) / 72.0
    px_width = font.getlength(text)
    # px_width is at _REF_PX; scale to font_pt, then px -> inches at 72dpi
    # (point-size fonts are defined in a 72-units-per-inch em square).
    return (px_width / _REF_PX) * font_pt / 72.0


def measure_width_in(text, font_pt, bold=False):
    """Public wrapper around the internal width measurement - used by
    the deck-level collision validator to check actual rendered text
    width rather than a shape's (often intentionally wider) box width."""
    return _measure_width_in(text, font_pt, bold)


def wrap_text(text, font_pt, max_width_in, bold=False):
    """
    Greedy word-wrap: returns the list of display lines `text` would
    occupy in a box `max_width_in` wide at `font_pt`. This mirrors how
    PowerPoint/LibreOffice actually wrap a text box, so the resulting
    line count is trustworthy for computing layout heights - unlike a
    character-count estimate.
    """
    if not text:
        return [""]
    words = str(text).split()
    if not words:
        return [""]

    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if _measure_width_in(candidate, font_pt, bold) <= max_width_in:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def line_height_in(font_pt, line_spacing=1.0):
    """
    Height of a single line at `font_pt` with the given line-spacing
    multiplier. 1.2 is the standard single-spacing line-height factor
    for Arial/Liberation Sans (ascent+descent+leading), matching what
    PowerPoint renders for line_spacing=1.0.
    """
    return (font_pt * 1.2 * line_spacing) / 72.0


def text_block_height_in(text, font_pt, max_width_in, bold=False, line_spacing=1.0, max_lines=None):
    """
    Total height in inches that `text` will occupy wrapped inside a box
    `max_width_in` wide. Optionally capped at `max_lines` (the caller is
    responsible for truncating the *text* itself if it wants the
    displayed content to match; this just bounds the height number).
    """
    lines = wrap_text(text, font_pt, max_width_in, bold)
    n = len(lines)
    if max_lines:
        n = min(n, max_lines)
    return line_height_in(font_pt, line_spacing) * max(1, n)


def count_wrapped_lines(text, font_pt, max_width_in, bold=False):
    return len(wrap_text(text, font_pt, max_width_in, bold))


def truncate_to_lines(text, font_pt, max_width_in, max_lines, bold=False, ellipsis="…"):
    """
    If `text` wraps to more than `max_lines` lines at `font_pt`, cut it
    at a word boundary so it fits in exactly `max_lines`, appending an
    ellipsis to the last line. Uses real wrapping, so the result is
    guaranteed to fit - not just "probably short enough".
    """
    lines = wrap_text(text, font_pt, max_width_in, bold)
    if len(lines) <= max_lines:
        return text, lines

    words = str(text).split()
    kept = []
    for i in range(len(words), 0, -1):
        candidate = " ".join(words[:i])
        candidate_lines = wrap_text(candidate + ellipsis, font_pt, max_width_in, bold)
        if len(candidate_lines) <= max_lines:
            kept = words[:i]
            break
    display = (" ".join(kept).rstrip(",.;:") + ellipsis) if kept else (words[0][: max(1, len(words[0]) - 1)] + ellipsis)
    return display, wrap_text(display, font_pt, max_width_in, bold)


def fit_text_to_box(text, max_width_in, max_lines, font_range, bold=False, step=2):
    """
    Returns (display_text, font_pt, line_count). Tries the largest font
    in font_range first and steps down; if the text still doesn't fit
    in max_lines at the smallest allowed size, truncates at a word
    boundary (via truncate_to_lines) instead of shrinking further -
    this is the "reduce font, then shorten, never overflow" priority
    order the layout brief calls for.
    """
    hi, lo = max(font_range), min(font_range)
    for font_pt in range(hi, lo - 1, -step):
        lines = wrap_text(text, font_pt, max_width_in, bold)
        if len(lines) <= max_lines:
            return text, font_pt, len(lines)
    display, lines = truncate_to_lines(text, lo, max_width_in, max_lines, bold)
    return display, lo, len(lines)


def shrink_to_single_line(text, max_width_in, font_pt, bold=False):
    """
    Word-boundary-trims `text` until it measures within `max_width_in`
    on one line at `font_pt`, guaranteeing a single-line result. Used
    for contexts (like Weekly Signals headlines) where the row's whole
    layout assumes a one-line header and we'd rather shorten the
    headline than let it wrap into the row below.
    """
    if _measure_width_in(text, font_pt, bold) <= max_width_in:
        return text
    words = str(text).split()
    for i in range(len(words) - 1, 0, -1):
        candidate = " ".join(words[:i]).rstrip(",.;:") + "…"
        if _measure_width_in(candidate, font_pt, bold) <= max_width_in:
            return candidate
    # Even a single word is too wide (pathological case) - hard character trim.
    word = words[0] if words else text
    while len(word) > 1 and _measure_width_in(word + "…", font_pt, bold) > max_width_in:
        word = word[:-1]
    return word + "…"
