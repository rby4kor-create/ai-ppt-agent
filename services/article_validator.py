class ArticleValidator:

    @staticmethod
    def is_valid(entry):

        if "title" not in entry:
            return False

        if "link" not in entry:
            return False

        return True