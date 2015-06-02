"""Written by - Rafal Kowalski"""
from flask.ext.admin.contrib.sqla import ModelView
from ....helpers.formatter import Formatter
from ....helpers.update_version import VersionUpdater


class SessionView(ModelView):
    column_formatters = {
        'title': Formatter.column_formatter,
        'subtile': Formatter.column_formatter,
        'abstract': Formatter.column_formatter,
        'description': Formatter.column_formatter,
        'type': Formatter.column_formatter,
        'level': Formatter.column_formatter,
    }

    def on_model_change(self, form, model, is_created):
        event_id = model.event_id
        if event_id:
            v = VersionUpdater(event_id=event_id, is_created=is_created, column_to_increment="session_ver")
            v.update()
