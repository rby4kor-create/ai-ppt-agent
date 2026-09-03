from difflib import SequenceMatcher


class DuplicateAgent:

    def remove_duplicates(
        self,
        articles,
        similarity_threshold=0.80
    ):

        unique_articles = []

        for article in articles:

            duplicate = False

            for existing in unique_articles:

                similarity = SequenceMatcher(
                    None,
                    article.title.lower(),
                    existing.title.lower()
                ).ratio()

                if similarity >= similarity_threshold:
                    duplicate = True
                    break

            if not duplicate:
                unique_articles.append(article)

        return unique_articles