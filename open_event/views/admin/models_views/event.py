"""Written by - Rafal Kowalski"""
from flask.ext.admin.contrib.sqla import ModelView
from ....helpers.formatter import Formatter
from ....helpers.update_version import VersionUpdater


class EventView(ModelView):

    column_formatters = {
        'name': Formatter.column_formatter,
        'location_name': Formatter.column_formatter
    }

    def on_model_change(self, form, model, is_created):
        try:
            v = VersionUpdater(event_id=model.id, is_created=is_created, column_to_increment="event_ver")
            v.update()
        except Exception as e:
            print e
