import flask_login
from flask import flash
from flask import make_response
from flask_login import current_user
from flask_admin import BaseView, expose

from app.views.admin.models_views.events import is_verified_user
from app.helpers.data_getter import DataGetter
from app.helpers.export import ExportHelper

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

    @expose('/pentabarf.xml')
    @flask_login.login_required
    def pentabarf_export_view(self, event_id):
        response = make_response(ExportHelper.export_as_pentabarf(event_id))
        response.headers["Content-Type"] = "application/xml"
        response.headers["Content-Disposition"] = "attachment; filename=pentabarf.xml"
        return response

    @expose('/calendar.ical')
    @flask_login.login_required
    def ical_export_view(self, event_id):
        response = make_response(ExportHelper.export_as_ical(event_id))
        response.headers["Content-Type"] = "text/calendar"
        response.headers["Content-Disposition"] = "attachment; filename=calendar.ics"
        return response

    @expose('/calendar.xcs')
    @flask_login.login_required
    def xcal_export_view(self, event_id):
        response = make_response(ExportHelper.export_as_xcal(event_id))
        response.headers["Content-Type"] = "text/calendar"
        response.headers["Content-Disposition"] = "attachment; filename=calendar.xcs"
        return response

