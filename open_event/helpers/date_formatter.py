"""Copyright 2015 Rafal Kowalski"""


class DateFormatter(object):
    """Date format class"""
    def format_date(self, date):
        """Return date with proper format"""
        return str(date.strftime("%Y-%m-%dT%H:%M:%S%Z"))


def operation_name(char):
    if char == 'c':
        return 'Create'
    elif char == 'r':
        return 'Read'
    elif char == 'u':
        return 'Update'
    elif char == 'd':
        return 'Delete'
