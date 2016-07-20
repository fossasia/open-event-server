import json

import flask_login
from flask import flash
from app.api import api
from flask_admin import BaseView, expose

from app.views.admin.models_views.events import is_verified_user
from ....helpers.data_getter import DataGetter

class ExportView(BaseView):

    @expose('/')
    @flask_login.login_required
    def display_api_view(self, event_id):
        event = DataGetter.get_event(event_id)
        if not is_verified_user():
            flash("Your account is unverified. "
                  "Please verify by clicking on the confirmation link that has been emailed to you.")
        return self.render('/gentelella/admin/event/export/export.html', event=event)
