from flask import Blueprint, abort, jsonify, make_response
from sqlalchemy.orm import make_transient

from app.api.helpers.db import safe_query, save_to_db
from app.api.helpers.permission_manager import has_access
from app.models import db
from app.models.custom_form import CustomForms
from app.models.discount_code import DiscountCode
from app.models.event import Event, get_new_event_identifier
from app.models.microlocation import Microlocation
from app.models.social_link import SocialLink
from app.models.speakers_call import SpeakersCall
from app.models.sponsor import Sponsor
from app.models.tax import Tax
from app.models.ticket import Ticket
from app.models.track import Track
from app.models.users_events_role import UsersEventsRoles

event_copy = Blueprint('event_copy', __name__, url_prefix='/v1/events')


def start_sponsor_logo_generation_task(event_id):
    from .helpers.tasks import sponsor_logos_url_task

    sponsor_logos_url_task.delay(event_id=event_id)


def copy_to_event(object, event):
    db.session.expunge(object)  # expunge the object
    make_transient(object)
    object.event_id = event.id
    delattr(object, 'id')
    save_to_db(object)


@event_copy.route('/<identifier>/copy', methods=['POST'])
def create_event_copy(identifier):
    id = 'identifier'

    if identifier.isdigit():
        id = 'id'

    event = safe_query(Event, id, identifier, 'event_' + id)

    if not has_access('is_coorganizer', event_id=event.id):
        return abort(make_response(jsonify(error="Access Forbidden"), 403))
    tickets = Ticket.query.filter_by(event_id=event.id, deleted_at=None).all()
    social_links = SocialLink.query.filter_by(event_id=event.id, deleted_at=None).all()
    sponsors = Sponsor.query.filter_by(event_id=event.id, deleted_at=None).all()
    microlocations = Microlocation.query.filter_by(
        event_id=event.id, deleted_at=None
    ).all()
    tracks = Track.query.filter_by(event_id=event.id, deleted_at=None).all()
    custom_forms = CustomForms.query.filter_by(event_id=event.id).all()
    discount_codes = DiscountCode.query.filter_by(
        event_id=event.id, deleted_at=None
    ).all()
    speaker_calls = SpeakersCall.query.filter_by(event_id=event.id, deleted_at=None).all()
    user_event_roles = UsersEventsRoles.query.filter_by(event_id=event.id).all()
    taxes = Tax.query.filter_by(event_id=event.id, deleted_at=None).all()

    db.session.expunge(event)  # expunge the object from session
    make_transient(event)
    delattr(event, 'id')
    event.identifier = get_new_event_identifier()
    save_to_db(event)

    # Ensure tax information is copied
    for tax in taxes:
        copy_to_event(tax, event)

    # Removes access_codes, order_tickets, ticket_tags for the new tickets created.
    for ticket in tickets:
        copy_to_event(ticket, event)

    for link in social_links:
        copy_to_event(link, event)

    for sponsor in sponsors:
        copy_to_event(sponsor, event)

    start_sponsor_logo_generation_task(event.id)

    for location in microlocations:
        copy_to_event(location, event)

    # No sessions are copied for new tracks
    for track in tracks:
        copy_to_event(track, event)

    for call in speaker_calls:
        copy_to_event(call, event)

    for code in discount_codes:
        copy_to_event(code, event)

    for form in custom_forms:
        copy_to_event(form, event)

    for user_role in user_event_roles:
        copy_to_event(user_role, event)

    return jsonify({'id': event.id, 'identifier': event.identifier, "copied": True})
