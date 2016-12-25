from flask import Blueprint
from flask import flash
from flask import make_response, render_template
from flask_login import current_user
from markupsafe import Markup

from app.helpers.data_getter import DataGetter
from app.helpers.auth import AuthManager
from app.helpers.exporters.ical import ICalExporter
from app.helpers.exporters.pentabarfxml import PentabarfExporter
from app.helpers.exporters.xcal import XCalExporter
from app.helpers.permission_decorators import can_access

event_export = Blueprint('event_export', __name__, url_prefix='/events/<int:event_id>/export')


@event_export.route('/')
@can_access
def display_export_view(event_id):
    event = DataGetter.get_event(event_id)
    export_jobs = DataGetter.get_export_jobs(event_id)
    user = current_user
    if not AuthManager.is_verified_user():
        flash(Markup("Your account is unverified. "
                     "Please verify by clicking on the confirmation link that has been emailed to you."
                     '<br>Did not get the email? Please <a href="/resend_email/" class="alert-link"> '
                     'click here to resend the confirmation.</a>'))
    return render_template(
        'gentelella/admin/event/export/export.html', event=event, export_jobs=export_jobs,
        current_user=user
    )


@event_export.route('/pentabarf.xml')
@can_access
def pentabarf_export_view(event_id):
    response = make_response(PentabarfExporter.export(event_id))
    response.headers["Content-Type"] = "application/xml"
    response.headers["Content-Disposition"] = "attachment; filename=pentabarf.xml"
    return response


@event_export.route('/calendar.ical')
@can_access
def ical_export_view(event_id):
    response = make_response(ICalExporter.export(event_id))
    response.headers["Content-Type"] = "text/calendar"
    response.headers["Content-Disposition"] = "attachment; filename=calendar.ics"
    return response


@event_export.route('/calendar.xcs')
@can_access
def xcal_export_view(event_id):
    response = make_response(XCalExporter.export(event_id))
    response.headers["Content-Type"] = "text/calendar"
    response.headers["Content-Disposition"] = "attachment; filename=calendar.xcs"
    return response
