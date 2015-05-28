from flask.ext.admin.contrib.sqla import ModelView
from ....helpers.formatter import Formatter


class SpeakerView(ModelView):
    # column_list = ('name', 'email',)
    column_formatters = {
        'name': Formatter.column_formatter,
        'email': Formatter.column_formatter,
        'photo': Formatter.column_formatter,
        'biography': Formatter.column_formatter,
        'web': Formatter.column_formatter,
        'twitter': Formatter.column_formatter,
        'facebook': Formatter.column_formatter,
        'github': Formatter.column_formatter,
        'linkedin': Formatter.column_formatter,
        'organisation': Formatter.column_formatter,
        'position': Formatter.column_formatter,
        'country': Formatter.column_formatter,
    }
