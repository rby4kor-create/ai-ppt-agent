class ResearchResult:

    def __init__(self):

        self.articles = []
        self.statistics = {}

        # [{source, title, reason}, ...] - articles seen in the feed but
        # dropped before reaching self.articles (missing fields, outside
        # date range, etc.), used for Problem 2's pipeline diagnostics.
        self.skipped = []
