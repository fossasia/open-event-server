"""Written by - Rafal Kowalski"""
from flask.ext.admin.contrib.sqla import ModelView
from ....helpers.formatter import Formatter
from ....helpers.update_version import VersionUpdater


class SpeakerView(ModelView):
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
        'country': Formatter.column_formatter}

    def on_model_change(self, form, model, is_created):
        event_id = model.event_id
        if event_id:
            v = VersionUpdater(event_id=event_id, is_created=is_created, column_to_increment="speakers_ver")
            v.update()
