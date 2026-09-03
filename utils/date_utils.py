from datetime import datetime
from email.utils import parsedate_to_datetime


class DateUtils:

    @staticmethod
    def parse_date(published: str):
        """
        Parses an RSS 'published' string (typically RFC 2822) into a
        naive datetime. Falls back to now() if parsing fails so a bad
        feed entry never crashes the pipeline.
        """

        if not published:
            return datetime.now()

        try:
            dt = parsedate_to_datetime(published)

            if dt.tzinfo is not None:
                dt = dt.replace(tzinfo=None)

            return dt

        except (TypeError, ValueError):
            return datetime.now()

    @staticmethod
    def is_between(article_date, start_date, end_date):

        return start_date <= article_date <= end_date
