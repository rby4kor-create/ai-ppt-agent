from models.article import Article
from utils.date_utils import DateUtils


class MetadataService:

    @staticmethod
    def create_article(source, entry):

        published = entry.get("published", "")

        article_date = DateUtils.parse_date(published)

        return Article(
            source=source,
            title=entry.title,
            link=entry.link,
            published=article_date
        )