"""Written by - Rafal Kowalski"""


class DateFormatter(object):

    def format_date(self, date):
        return str(date.strftime("%Y-%m-%dT%H:%M:%S%Z"))
