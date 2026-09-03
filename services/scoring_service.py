from datetime import datetime


class ScoringService:
    """
    Heuristic relevance score for an article. Higher is more
    interesting for an enterprise GenAI weekly report.
    """

    HIGH_VALUE_KEYWORDS = [
        "launch", "release", "announce", "partnership", "enterprise",
        "funding", "acquisition", "benchmark", "breakthrough", "update"
    ]

    STRATEGIC_SOURCES = {
        "OpenAI": 1.15,
        "Anthropic": 1.15,
        "Google DeepMind": 1.1,
        "Microsoft AI": 1.05,
        "NVIDIA": 1.05,
    }

    @staticmethod
    def calculate_score(article) -> float:

        score = 50.0

        title = (article.title or "").lower()

        for keyword in ScoringService.HIGH_VALUE_KEYWORDS:
            if keyword in title:
                score += 8

        score *= ScoringService.STRATEGIC_SOURCES.get(article.source, 1.0)

        if getattr(article, "published", None):
            days_old = max((datetime.now() - article.published).days, 0)
            score -= min(days_old * 1.5, 15)

        return round(score, 2)
