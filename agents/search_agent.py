import feedparser

from models.article import Article
from models.research_result import ResearchResult
from config import RSS_FEEDS
from utils.date_utils import DateUtils
from utils.logger import get_logger

logger = get_logger(__name__)


class SearchAgent:

    def fetch_articles(
        self,
        start_date,
        end_date,
        max_articles_per_source=20,
        feeds=None,
    ):

        result = ResearchResult()
        feeds = feeds if feeds is not None else RSS_FEEDS

        for source, url in feeds.items():

            logger.info(f"Checking {source}...")

            try:
                feed = feedparser.parse(url)

                if getattr(feed, "bozo", False) and not feed.entries:
                    logger.warning(f"{source}: feed failed to parse ({feed.bozo_exception})")
                    result.statistics[source] = 0
                    continue

                count = 0

                for entry in feed.entries[:max_articles_per_source]:

                    title = entry.get("title", "")
                    link = entry.get("link", "")
                    if not title or not link:
                        result.skipped.append({
                            "source": source, "title": title or "(no title)",
                            "reason": "missing title or link",
                        })
                        continue

                    published = entry.get("published", "") or entry.get("updated", "")
                    article_date = DateUtils.parse_date(published)

                    if not DateUtils.is_between(article_date, start_date, end_date):
                        result.skipped.append({
                            "source": source, "title": title,
                            "reason": f"outside date range (parsed: {article_date.date()})",
                        })
                        continue

                    raw_content = entry.get("summary", "") or entry.get("description", "")

                    article = Article(
                        source=source,
                        title=title,
                        link=link,
                        published=article_date,
                        raw_content=raw_content,
                    )

                    result.articles.append(article)
                    count += 1

                result.statistics[source] = count

            except Exception as ex:
                logger.error(f"{source}: fetch failed - {ex}")
                result.statistics[source] = 0

        return result
