"""Copyright 2015 Rafal Kowalski"""


class DateFormatter(object):
    """Date format class"""
    def format_date(self, date):
        """Return date with proper format"""
        return str(date.strftime("%Y-%m-%dT%H:%M:%S%Z"))
