from newspaper import Article


class ArticleFetcher:

    """
    Downloads and extracts the main text from an article URL.
    """

    def fetch(self, url: str) -> str:

        try:
            article = Article(url)

            article.download()
            article.parse()

            return article.text

        except Exception as e:

            print(f"[ArticleFetcher] Failed: {url}")

            print(e)

            return ""
        