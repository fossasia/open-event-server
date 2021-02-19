from flask import request
from flask.blueprints import Blueprint
from flask.helpers import make_response
from flask_jwt_extended.view_decorators import jwt_optional

from app.api.helpers.calendar.ical import to_ical
from app.api.helpers.permissions import to_event_id
from app.models.event import Event

calendar_routes = Blueprint('calendars', __name__, url_prefix='/v1/events')


@calendar_routes.route(
    '/<string:event_identifier>.ics',
)
@to_event_id
@jwt_optional
def export_event(event_id):
    event = Event.query.get_or_404(event_id)
    include_sessions = 'include_sessions' in request.args
    my_schedule = 'my_schedule' in request.args
    user_id = request.args.get('user_id')

    response = to_ical(
        event, include_sessions=include_sessions, my_schedule=my_schedule, user_id=user_id
    )

    response = make_response(response)
    response.headers['Content-Type'] = 'text/calendar'
    if 'download' in request.args:
        response.headers[
            'Content-Disposition'
        ] = f'attachment; filename={event.identifier}-{event.name}-Calendar.ics;'
        response.headers['Content-Type'] = 'octet/stream'

    return response
