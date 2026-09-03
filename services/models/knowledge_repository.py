class KnowledgeRepository:

    def __init__(self):

        self.categories = {}

    def add_article(self, article):

        category = article.category

        if category not in self.categories:
            self.categories[category] = []

        self.categories[category].append(article)

    def get_categories(self):

        return self.categories