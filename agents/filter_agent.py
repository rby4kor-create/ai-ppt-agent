class FilterAgent:

    def filter_by_week(self, articles, week):

        filtered = []

        for article in articles:

            if article["calendar_week"] == week:

                filtered.append(article)

        return filtered