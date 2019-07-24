from flask import Blueprint, jsonify
from app.models.event import Event
from sqlalchemy.orm.exc import NoResultFound
from app.api.helpers.errors import NotFoundError


event_components = Blueprint('event_components', __name__, url_prefix='/v1/event/components')


@event_components.route('/<event_id>/<component>', methods=['POST', 'GET'])
def components(event_id, component):
    try:
        event = Event.query.filter_by(id=event_id).one()
    except NoResultFound:
        return NotFoundError({'source': ''}, 'Event Not Found').respond()

    if component == 'tickets':
        if not event.tickets_available:
            return NotFoundError({'source': ''}, 'No tickets are linked to this event').respond()

    elif component == 'session':
        if not event.has_sessions:
            return NotFoundError({'source': ''}, 'No sessions are linked to this event').respond()

    elif component == 'speakers':
        if not event.has_speakers:
            return NotFoundError({'source': ''}, 'No speakers are present for this event').respond()

    return jsonify({"status": True})
