"""Written by - Rafal Kowalski"""
from flask.ext.admin.contrib.sqla import ModelView
from ....helpers.formatter import Formatter


class SessionView(ModelView):
    column_formatters = {
        'title': Formatter.column_formatter,
        'subtile': Formatter.column_formatter,
        'abstract': Formatter.column_formatter,
        'description': Formatter.column_formatter,
        'type': Formatter.column_formatter,
        'level': Formatter.column_formatter,
    }
