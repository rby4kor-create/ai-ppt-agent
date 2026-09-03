class ExecutiveAnalysis:
    """
    Single, consistent data contract for per-article analysis, regardless
    of whether it was produced by LLMService (real LLM call) or
    TemplateAnalysisAgent (deterministic offline fallback). Every field
    listed here is guaranteed to exist with a safe default, so downstream
    code (PresentationBuilder, PowerPointAgent) never needs to guess
    whether a field is present - this is the fix for the
    "ExecutiveAnalysis.__init__() missing: strategic_importance"-class
    bug: the schema is defined in exactly one place, and both producers
    (LLM parser, template fallback) are required to fill it completely.
    """

    def __init__(
        self,
        title="",
        category="",
        source="",
        article_url="",
        published=None,
        # Core narrative fields
        executive_summary="",
        business_impact="",
        technical_analysis="",
        enterprise_recommendation="",
        future_outlook="",
        strategic_importance="",
        # Scores
        innovation_score=5.0,          # 0-10
        enterprise_readiness=5,        # 0-10
        confidence_score=0.7,          # 0-1
        risk_level="Medium",           # Low / Medium / High
        implementation_effort="Medium",
        # Lists
        key_takeaways=None,
        key_technologies=None,
        keywords=None,
        industry_impact=None,
        opportunities=None,
        risks=None,
        # Provenance
        generated_by="template",       # "llm" or "template" - shown nowhere in
                                        # the deck, but useful for QA/logging to
                                        # confirm which path actually produced
                                        # the content for a given slide.
    ):
        self.title = title
        self.category = category
        self.source = source
        self.article_url = article_url
        self.published = published

        self.executive_summary = executive_summary
        self.business_impact = business_impact
        self.technical_analysis = technical_analysis
        self.enterprise_recommendation = enterprise_recommendation
        self.future_outlook = future_outlook
        self.strategic_importance = strategic_importance

        self.innovation_score = self._clamp(innovation_score, 0, 10)
        self.enterprise_readiness = self._clamp(enterprise_readiness, 0, 10)
        self.confidence_score = self._clamp(confidence_score, 0, 1)
        self.risk_level = risk_level if risk_level in ("Low", "Medium", "High") else "Medium"
        self.implementation_effort = implementation_effort or "Medium"

        self.key_takeaways = key_takeaways or []
        self.key_technologies = key_technologies or []
        self.keywords = keywords or []
        self.industry_impact = industry_impact or []
        self.opportunities = opportunities or []
        self.risks = risks or []

        self.generated_by = generated_by

    @staticmethod
    def _clamp(value, lo, hi):
        try:
            value = float(value)
        except (TypeError, ValueError):
            return lo
        return max(lo, min(hi, value))

    def is_valid(self):
        """Minimal content validation per the pipeline's QA requirements."""
        if not self.title or not self.source:
            return False, "missing title or source"
        if not self.executive_summary:
            return False, "missing executive_summary"
        if self.risk_level not in ("Low", "Medium", "High"):
            return False, f"invalid risk_level: {self.risk_level}"
        if not (0 <= self.innovation_score <= 10):
            return False, f"innovation_score out of range: {self.innovation_score}"
        if not (0 <= self.confidence_score <= 1):
            return False, f"confidence_score out of range: {self.confidence_score}"
        return True, ""
