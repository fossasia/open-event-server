"""Written by - Rafal Kowalski"""
from flask.ext.admin.contrib.sqla import ModelView
from ....helpers.formatter import Formatter


class EventView(ModelView):
    column_formatters = {
        'name': Formatter.column_formatter,
        'location_name': Formatter.column_formatter
    }
