from config import MAX_SELECTED_TOPICS


class TopicSelectionAgent:
    """
    Selects up to `max_topics` articles across all categories, capping
    at 2 per source so one prolific source can't crowd out the rest,
    then filling any remaining slots regardless of source. Never
    fabricates articles: if fewer than max_topics valid articles exist
    across the whole repository, fewer are returned - the deck simply
    has fewer topic slides (see run_pipeline diagnostics in app.py).
    """

    def select_topics(self, repository, max_topics=MAX_SELECTED_TOPICS):

        selected = []
        company_count = {}

        all_articles = []
        for category, articles in repository.get_categories().items():
            articles = sorted(articles, key=lambda x: x.score, reverse=True)
            all_articles.extend(articles)

        # First pass: max 2 per source
        for article in all_articles:
            company = article.source
            company_count.setdefault(company, 0)

            if company_count[company] >= 2:
                continue

            selected.append(article)
            company_count[company] += 1

            if len(selected) >= max_topics:
                return selected

        # Second pass: fill remaining slots regardless of source
        for article in all_articles:
            if article in selected:
                continue

            selected.append(article)

            if len(selected) >= max_topics:
                break

        return selected
