from datetime import datetime


class Article:
    """
    Raw collected article + pipeline bookkeeping fields (score, category).
    Narrative/analysis content (summary, business impact, strategic
    observation, scores, etc.) intentionally does NOT live here anymore -
    it lives in a separate ExecutiveAnalysis object produced by
    AnalysisAgent, one per selected article. Keeping "raw collected data"
    and "generated analysis" as two separate objects is what makes the
    LLM-output/data-model contract enforceable in one place
    (models/executive_analysis.py) instead of two.
    """

    def __init__(
        self,
        source: str,
        title: str,
        link: str,
        published: datetime,
        raw_content: str = "",
    ):

        self.source = source
        self.title = title
        self.link = link
        self.published = published

        # The RSS entry's own summary/description text (NOT the full
        # article body - no network fetch of the article page is done).
        # This is real, source-provided text distinct from the title, and
        # is what gets passed to the LLM as "article_text" so analysis is
        # grounded in more than just a headline.
        self.raw_content = raw_content or ""

        # Filled in by RankingAgent / CategorizationAgent
        self.score = 0
        self.category = ""
        self.category_confidence = 0.0

    def __str__(self):
        return (
            f"{self.source} | "
            f"{self.title} | "
            f"{self.published.strftime('%d-%b-%Y')}"
        )
