import flask_login
from flask import flash
from flask_login import current_user
from flask_admin import BaseView, expose

from app.views.admin.models_views.events import is_verified_user
from ....helpers.data_getter import DataGetter


class ExportView(BaseView):
    @expose('/')
    @flask_login.login_required
    def display_export_view(self, event_id):
        event = DataGetter.get_event(event_id)
        export_jobs = DataGetter.get_export_jobs(event_id)
        user = current_user
        if not is_verified_user():
            flash("Your account is unverified. "
                  "Please verify by clicking on the confirmation link that has been emailed to you.")
        return self.render(
            '/gentelella/admin/event/export/export.html', event=event, export_jobs=export_jobs,
            current_user=user
        )
