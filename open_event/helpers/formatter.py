"""Copyright 2015 Rafal Kowalski"""


class Formatter(object):

    @staticmethod
    def column_formatter(view, context, model, name):
        value = getattr(model, name)
        if value:
            return value if len(value) < 10 else value[0:10] + ' ...'
        return ''
