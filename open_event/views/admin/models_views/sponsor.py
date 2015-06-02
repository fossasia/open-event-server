"""Written by - Rafal Kowalski"""
from flask.ext.admin.contrib.sqla import ModelView
from ....helpers.formatter import Formatter
from ....helpers.update_version import VersionUpdater


class SponsorView(ModelView):
    column_formatters = {
        'name': Formatter.column_formatter,
        'url': Formatter.column_formatter,
        'logo': Formatter.column_formatter}

    def on_model_change(self, form, model, is_created):
        event_id = model.event_id
        if event_id:
            v = VersionUpdater(event_id=event_id, is_created=is_created, column_to_increment="sponsors_ver")
            v.update()