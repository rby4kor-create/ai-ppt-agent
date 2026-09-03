class SourceStatistics:

    def __init__(self):

        self.statistics = {}

    def increment(self, source):

        self.statistics[source] = self.statistics.get(source, 0) + 1

    def get_statistics(self):

        return self.statistics