from services.scoring_service import ScoringService


class RankingAgent:

    def rank_articles(self, articles):

        for article in articles:

            article.score = ScoringService.calculate_score(article)

        ranked_articles = sorted(
            articles,
            key=lambda article: article.score,
            reverse=True
        )

        return ranked_articles