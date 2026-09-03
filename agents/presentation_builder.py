import os
from datetime import datetime
from collections import defaultdict

from config import MIN_TOPICS_FOR_SECTION_DIVIDER
from models.presentation import Presentation
from models.slide import Slide
from agents.image_agent import ImageAgent
from agents.powerpoint_agent import smart_shorten_title
from utils.logger import get_logger

logger = get_logger(__name__)


class PresentationBuilder:
    """
    Converts a list of ExecutiveAnalysis objects (one per selected
    article) into the full Presentation model PowerPointAgent renders:
    groups topics into category sections (with dividers where a category
    has enough topics), computes executive-overview stats, derives
    weekly signals and strategic takeaways, and resolves each topic's
    image via ImageAgent.
    """

    def __init__(self):
        self.image_agent = ImageAgent()

    def build(self, analyses, executive_summary, image_overrides=None):
        self.image_agent.reset_usage()  # fresh "avoid repeating an image" tracking for this deck
        image_overrides = image_overrides or {}

        presentation = Presentation()
        now = datetime.now()
        # ISO calendar week, e.g. "CW28, 2026" - matches the naming/branding
        # used by the TopGenAI-CWxx-2026.pptx reference decks, so both the
        # cover title and the small per-slide corner tag stay consistent
        # with the report's actual filename convention instead of a
        # generic "Weekly ... Report" title.
        iso_year, iso_week, _ = now.isocalendar()
        presentation.week_label = f"CW{iso_week:02d}, {iso_year}"
        presentation.title = f"Top Gen AI Advances: {presentation.week_label}"
        presentation.subtitle = "AI Executive Briefing"
        presentation.generated_date = now.strftime("%d %B %Y")
        presentation.executive_summary = executive_summary

        # --- Executive overview stats -----------------------------------
        categories = sorted({a.category for a in analyses})
        avg_innovation = (
            sum(a.innovation_score for a in analyses) / len(analyses) if analyses else 0
        )
        risk_flags = sum(1 for a in analyses if a.risk_level == "High")

        presentation.exec_stats = {
            "Developments": str(len(analyses)),
            "Domains": str(len(categories)),
            "Avg. Innovation": f"{avg_innovation:.1f}",
            "Risk Flags": str(risk_flags),
        }

        # Order themes by how many topics fall in each category (most first)
        by_category = defaultdict(list)
        for a in analyses:
            by_category[a.category].append(a)
        presentation.exec_themes = [
            cat for cat, items in sorted(by_category.items(), key=lambda kv: -len(kv[1]))
        ]

        # --- Weekly signals (top-scoring items, one per category where
        # possible, ranked by innovation score) -------------------------
        top_ranked = sorted(analyses, key=lambda a: a.innovation_score, reverse=True)
        seen_categories = set()
        signals = []
        for a in top_ranked:
            if len(signals) >= 4:
                break
            if a.category in seen_categories and len(seen_categories) < len(by_category):
                continue
            seen_categories.add(a.category)
            impact = "High" if a.innovation_score >= 8 else ("Medium" if a.innovation_score >= 6 else "Low")
            signals.append({
                "headline": smart_shorten_title(a.title, max_words=14),
                "explanation": a.executive_summary,
                "impact": impact,
            })
        presentation.weekly_signals = signals

        # --- Topic slides, grouped into sections -------------------------
        slide_number = 1
        sections = []
        for category in presentation.exec_themes:
            items = by_category[category]
            slides = []
            for analysis in items:
                slide = self._build_slide(analysis, slide_number, image_overrides)
                slides.append(slide)
                presentation.add_slide(slide)
                presentation.references.append({
                    "source": analysis.source,
                    "title": analysis.title,
                    "link": analysis.article_url,
                })
                slide_number += 1

            sections.append({
                "category": category,
                "needs_divider": len(items) >= MIN_TOPICS_FOR_SECTION_DIVIDER,
                "slides": slides,
            })
        presentation.sections = sections

        # --- Strategic takeaways ------------------------------------------
        presentation.strategic_takeaways = self._build_takeaways(analyses, by_category)

        return presentation

    def _build_slide(self, analysis, slide_number, image_overrides=None):
        slide = Slide()
        slide.category = analysis.category
        slide.source_title = analysis.title
        slide.title = smart_shorten_title(analysis.title, max_words=13)

        bullets = []
        if analysis.business_impact:
            bullets.append(analysis.business_impact)
        if analysis.technical_analysis:
            bullets.append(analysis.technical_analysis)
        if analysis.future_outlook:
            bullets.append(analysis.future_outlook)
        elif analysis.key_takeaways:
            bullets.extend(analysis.key_takeaways)
        slide.summary = bullets[:3]

        slide.strategic_observation = analysis.strategic_importance
        slide.recommendation = analysis.enterprise_recommendation

        slide.key_technologies = analysis.key_technologies[:4]
        slide.innovation_score = analysis.innovation_score
        slide.risk_level = analysis.risk_level
        slide.enterprise_readiness = self._readiness_label(analysis.enterprise_readiness)

        override_path = (image_overrides or {}).get(analysis.article_url)
        if override_path and os.path.exists(override_path):
            slide.image_path = override_path
        else:
            slide.image_path = self.image_agent.resolve_image_path(
                analysis.category, title=analysis.title, keywords=analysis.key_technologies,
            )
        slide.visual_type = analysis.category

        slide.source = analysis.source
        slide.source_link = analysis.article_url
        slide.notes = analysis.executive_summary

        slide.slide_number = slide_number
        return slide

    @staticmethod
    def _readiness_label(score):
        try:
            score = float(score)
        except (TypeError, ValueError):
            return "Monitor"
        if score >= 8:
            return "Production-ready"
        if score >= 6:
            return "Pilot-ready"
        if score >= 4:
            return "Early pilot"
        if score >= 2:
            return "Planning stage"
        return "Monitor"

    def _build_takeaways(self, analyses, by_category):
        """
        Builds up to 5 non-repeating leadership-brief rows. Each candidate
        below is tagged with the category (if any) it's "about"; once a
        category has been used for one takeaway it's skipped for every
        other category-scoped candidate, so with only 1-2 categories in
        play (a common case for a slow week) the slide no longer shows
        near-identical "X produced the most / X has the highest score"
        rows back to back. Category-agnostic candidates (risk, readiness,
        breadth, source concentration) always remain eligible and are
        used to fill out the slide when category diversity is low.
        """
        if not analyses:
            return []

        used_categories = set()
        candidates = []  # list of (category_or_None, dict)

        # 1. Largest category by topic count
        top_category, top_items = max(by_category.items(), key=lambda kv: len(kv[1]))
        candidates.append((top_category, {
            "signal": f"{top_category} produced the most developments this week ({len(top_items)}).",
            "implication": "This domain is moving faster than others and is likely where competitive gaps open first.",
            "action": f"Prioritize a capability review in {top_category} this quarter.",
        }))

        # 2. Highest average innovation category
        avg_by_cat = {
            cat: sum(a.innovation_score for a in items) / len(items)
            for cat, items in by_category.items()
        }
        best_cat = max(avg_by_cat, key=avg_by_cat.get)
        candidates.append((best_cat, {
            "signal": f"{best_cat} shows the highest average innovation score this week ({avg_by_cat[best_cat]:.1f}/10).",
            "implication": "Capability in this domain is advancing faster than the rest of the market average.",
            "action": f"Benchmark current vendors in {best_cat} against this week's developments.",
        }))

        # 3. Risk flags (category-agnostic)
        high_risk = [a for a in analyses if a.risk_level == "High"]
        if high_risk:
            candidates.append((None, {
                "signal": f"{len(high_risk)} item(s) this week carry a High risk/governance flag.",
                "implication": "Deployment or procurement decisions touching these areas need governance sign-off first.",
                "action": "Route flagged items through security/governance review before any pilot expands.",
            }))

        # 4. Production-ready items (category-agnostic)
        ready = [a for a in analyses if a.enterprise_readiness and float(a.enterprise_readiness) >= 8]
        if ready:
            candidates.append((None, {
                "signal": f"{len(ready)} development(s) are already assessed as production-ready.",
                "implication": "These require no additional pilot phase to start delivering value.",
                "action": "Fast-track evaluation for teams with an immediate use case.",
            }))

        # 5. Domain breadth (category-agnostic)
        candidates.append((None, {
            "signal": f"Developments this week span {len(by_category)} distinct technology domain(s).",
            "implication": "Broad movement across domains suggests no single competitive front to watch." if len(by_category) > 1
                           else "Activity is concentrated in a single domain this week rather than spread across the market.",
            "action": "Assign domain owners to monitor each area independently rather than centralizing tracking." if len(by_category) > 1
                       else f"Deepen monitoring within {next(iter(by_category))} rather than spreading coverage thin.",
        }))

        # 6. Source concentration (category-agnostic fallback - keeps the
        # slide at 5 rows even on weeks with a single, narrow category)
        by_source = defaultdict(list)
        for a in analyses:
            by_source[a.source].append(a)
        if by_source:
            top_source, top_source_items = max(by_source.items(), key=lambda kv: len(kv[1]))
            candidates.append((None, {
                "signal": f"{top_source} was the most active source this week ({len(top_source_items)} development(s)).",
                "implication": "Concentration in one lab/vendor's release cadence is worth tracking for roadmap signal.",
                "action": f"Add {top_source}'s roadmap and release notes to standing competitive watch.",
            }))

        # 7. Second-largest category, only if it exists and differs from #1
        rest_by_size = sorted(
            ((cat, items) for cat, items in by_category.items() if cat != top_category),
            key=lambda kv: -len(kv[1]),
        )
        if rest_by_size:
            second_cat, second_items = rest_by_size[0]
            candidates.append((second_cat, {
                "signal": f"{second_cat} was the second most active domain this week ({len(second_items)}).",
                "implication": "A secondary domain building momentum alongside the leader broadens near-term exposure.",
                "action": f"Assign a secondary owner to track {second_cat} in parallel.",
            }))

        takeaways = []
        for category, item in candidates:
            if category is not None and category in used_categories:
                continue
            takeaways.append(item)
            if category is not None:
                used_categories.add(category)
            if len(takeaways) >= 5:
                break

        return takeaways[:5]
