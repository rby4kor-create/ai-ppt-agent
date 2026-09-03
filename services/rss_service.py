import feedparser


class RSSService:

    def fetch_feed(self, url):

        try:

            return feedparser.parse(url)

        except Exception:

            return None