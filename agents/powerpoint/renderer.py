"""
renderer.py

Central rendering engine for the PowerPoint framework.

Every slide builder and UI component receives a Renderer instance
instead of directly accessing python-pptx APIs.

Responsibilities
----------------
• Holds the Presentation object
• Tracks the active slide
• Provides access to Theme/Layout
• Creates slides
• Provides helper methods used across builders
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from pptx import Presentation
from pptx.slide import Slide

from .theme import Colors, Fonts, FontSize
from .layout import Page


class Renderer:
    """
    Rendering environment shared by all slide builders.

    Parameters
    ----------
    presentation:
        Active PowerPoint Presentation.

    assets_path:
        Folder containing icons, logos and placeholder images.
    """

    def __init__(
        self,
        presentation: Presentation,
        assets_path: str | Path = "assets",
    ):

        self.presentation = presentation

        self.assets_path = Path(assets_path)

        self.slide: Optional[Slide] = None

        # expose theme
        self.colors = Colors
        self.fonts = Fonts
        self.font_sizes = FontSize

        # expose layout
        self.page = Page

    # --------------------------------------------------------
    # Slide Management
    # --------------------------------------------------------

    def new_slide(self, layout_index: int = 6) -> Slide:
        """
        Create a blank slide.

        Returns
        -------
        Slide
        """

        layout = self.presentation.slide_layouts[layout_index]

        self.slide = self.presentation.slides.add_slide(layout)

        return self.slide

    # --------------------------------------------------------
    # Current Slide
    # --------------------------------------------------------

    def current_slide(self) -> Slide:
        """
        Return active slide.

        Raises
        ------
        RuntimeError
            If no slide exists.
        """

        if self.slide is None:
            raise RuntimeError(
                "Renderer has no active slide."
            )

        return self.slide

    # --------------------------------------------------------
    # Assets
    # --------------------------------------------------------

    def asset(self, filename: str) -> Path:
        """
        Return full asset path.
        """

        return self.assets_path / filename

    # --------------------------------------------------------
    # Slide Size
    # --------------------------------------------------------

    @property
    def slide_width(self):

        return self.presentation.slide_width

    @property
    def slide_height(self):

        return self.presentation.slide_height