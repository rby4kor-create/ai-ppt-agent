from datetime import datetime


class ResearchRequest:

    def __init__(
        self,
        topic,
        start_date,
        end_date,
        max_articles_per_source=20,
        final_articles=10
    ):

        self.topic = topic
        self.start_date = start_date
        self.end_date = end_date

        self.max_articles_per_source = max_articles_per_source
        self.final_articles = final_articles