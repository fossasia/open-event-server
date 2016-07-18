"""Copyright 2015 Rafal Kowalski"""


class Formatter(object):
    """Formatter class"""
    @staticmethod
    def column_formatter(view, context, model, name):
        """Column table formatter"""
        value = getattr(model, name)
        if value:
            return value if len(value) < 10 else value[0:10] + ' ...'
        return ''


def operation_name(char):
    if char == 'c':
        return 'Create'
    elif char == 'r':
        return 'Read'
    elif char == 'u':
        return 'Update'
    elif char == 'd':
        return 'Delete'
