from flask import request
from flask.blueprints import Blueprint
from flask.helpers import make_response

from app.api.helpers.calendar.ical import to_ical
from app.api.helpers.permissions import to_event_id
from app.models.event import Event

calendar_routes = Blueprint('calendars', __name__, url_prefix='/v1/events')


@calendar_routes.route(
    '/<string:event_identifier>.ics',
)
@to_event_id
def export_event(event_id):
    event = Event.query.get_or_404(event_id)
    include_sessions = 'include_sessions' in request.args
    download = 'download' in request.args

    response = to_ical(event, include_sessions=include_sessions)

    if download:
        response = make_response(response)
        response.headers[
            'Content-Disposition'
        ] = f'attachment; filename={event.identifier}-{event.name}-Calendar.ics;'
        response.headers['Content-Type'] = 'octet/stream'

    return response
