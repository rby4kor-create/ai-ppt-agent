from models.knowledge_repository import KnowledgeRepository


class KnowledgeAgent:

    def build_repository(self, articles):

        repository = KnowledgeRepository()

        for article in articles:
            repository.add_article(article)

        return repository