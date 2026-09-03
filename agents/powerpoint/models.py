"""
models.py

Data models used throughout the PowerPoint rendering engine.

These classes provide a strongly-typed interface between the
PresentationBuilder and all slide builders.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Dict


# ---------------------------------------------------------
# Basic Metadata
# ---------------------------------------------------------

@dataclass(slots=True)
class Source:
    """Represents a reference or citation."""

    name: str
    url: str


@dataclass(slots=True)
class Badge:
    """Small visual label."""

    text: str
    color: str = "primary"


# ---------------------------------------------------------
# Cards
# ---------------------------------------------------------

@dataclass(slots=True)
class Card:
    """
    Generic reusable card.
    """

    title: str
    body: str

    icon: Optional[str] = None

    badges: List[Badge] = field(default_factory=list)


# ---------------------------------------------------------
# Topic Slide
# ---------------------------------------------------------

@dataclass(slots=True)
class TopicContext:
    """
    Data required for rendering one technology/topic slide.
    """

    title: str

    category: str

    summary: str

    enterprise_relevance: str

    image_path: Optional[str] = None

    source_name: str = ""

    source_link: str = ""

    notes: str = ""

    innovation_score: Optional[float] = None

    confidence: Optional[float] = None

    tags: List[str] = field(default_factory=list)

    recommendations: List[str] = field(default_factory=list)


# ---------------------------------------------------------
# Executive Summary
# ---------------------------------------------------------

@dataclass(slots=True)
class ExecutiveSummaryContext:

    summary: str

    key_points: List[str] = field(default_factory=list)

    recommendations: List[str] = field(default_factory=list)


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

@dataclass(slots=True)
class DashboardContext:

    total_articles: int

    total_sources: int

    avg_innovation_score: float

    enterprise_ready: int

    high_risk: int

    medium_risk: int

    low_risk: int

    top_technologies: List[str]


# ---------------------------------------------------------
# Cover
# ---------------------------------------------------------

@dataclass(slots=True)
class CoverContext:

    title: str

    subtitle: str

    report_date: str

    organization: str

    logo_path: Optional[str] = None


# ---------------------------------------------------------
# References
# ---------------------------------------------------------

@dataclass(slots=True)
class ReferenceContext:

    references: List[Source]


# ---------------------------------------------------------
# Whole Presentation
# ---------------------------------------------------------

@dataclass(slots=True)
class PresentationContext:
    """
    Entire report passed into the rendering engine.
    """

    cover: CoverContext

    dashboard: DashboardContext

    executive_summary: ExecutiveSummaryContext

    topics: List[TopicContext]

    references: ReferenceContext

    metadata: Dict[str, str] = field(default_factory=dict)