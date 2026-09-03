from services.article_fetcher import ArticleFetcher
from services.llm_service import LLMService


class ArticleAnalyzer:
    """
    Coordinates article fetching and AI analysis.
    """

    def __init__(self):
        self.fetcher = ArticleFetcher()
        self.llm = LLMService()

    def analyze(self, article):
        """
        Downloads the article and generates executive analysis.
        """

        article_text = self.fetcher.fetch(article.link)

        if not article_text:
            raise ValueError(
                f"Could not fetch article: {article.title}"
            )

        return self.llm.generate_analysis(
            article,
            article_text
        )