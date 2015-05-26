from flask.ext.admin.contrib.sqla import ModelView
from ....helpers.formatter import Formatter


class SponsorView(ModelView):
    column_formatters = {
        'name': Formatter.column_formatter,
        'url': Formatter.column_formatter,
        'logo': Formatter.column_formatter
    }
