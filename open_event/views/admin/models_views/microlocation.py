"""Written by - Rafal Kowalski"""
from flask.ext.admin.contrib.sqla import ModelView
from ....helpers.update_version import VersionUpdater


class MicrolocationView(ModelView):
    def on_model_change(self, form, model, is_created):
        event_id = model.event_id
        if event_id:
            v = VersionUpdater(event_id=event_id, is_created=is_created, column_to_increment="microlocations_ver")
            v.update()
