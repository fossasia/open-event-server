from datetime import date

from flask_rest_jsonapi.data_layers.base import BaseDataLayer
from sqlalchemy.orm import make_transient

from app.api.helpers.db import safe_query, save_to_db
from app.api.helpers.files import create_save_resized_image
from app.models.custom_form import CustomForms
from app.models.discount_code import DiscountCode
from app.models.event import Event, get_new_event_identifier
from app.models import db
from app.models.microlocation import Microlocation
from app.models.social_link import SocialLink
from app.models.speakers_call import SpeakersCall
from app.models.sponsor import Sponsor
from app.models.ticket import Ticket
from app.models.track import Track


def update_created_at(obj):
    if type(object) is list:
        for o in obj:
            o.created_at = date.now()


class EventCopyLayer(BaseDataLayer):

    def create_object(self, data, view_kwargs):
        identifier = 'identifier'

        if view_kwargs.get('identifier').isdigit():
            identifier = 'id'

        event = safe_query(db, Event, identifier, view_kwargs['identifier'], 'event_'+identifier)
        tickets = Ticket.query.filter_by(event_id=event.id).all()
        social_links = SocialLink.query.filter_by(event_id=event.id).all()
        sponsors = Sponsor.query.filter_by(event_id=event.id).all()
        microlocations = Microlocation.query.filter_by(event_id=event.id).all()
        tracks = Track.query.filter_by(event_id=event.id).all()
        custom_forms = CustomForms.query.filter_by(event_id=event.id).all()
        discount_codes = DiscountCode.query.filter_by(event_id=event.id).all()
        speaker_calls = SpeakersCall.query.filter_by(event_id=event.id).all()

        db.session.expunge(event)  # expunge the object from session
        make_transient(event)
        delattr(event, 'id')
        event.identifier = get_new_event_identifier()
        save_to_db(event)

        # Removes access_codes, order_tickets, ticket_tags for the new tickets created.
        for ticket in tickets:
            ticket_id = ticket.id
            db.session.expunge(ticket)  # expunge the object from session
            make_transient(ticket)
            ticket.event_id = event.id
            delattr(ticket, 'id')
            save_to_db(ticket)

        for link in social_links:
            link_id = link.id
            db.session.expunge(link)  # expunge the object from session
            make_transient(link)
            link.event_id = event.id
            delattr(link, 'id')
            save_to_db(link)

        for sponsor in sponsors:
            sponsor_id = sponsor.id
            db.session.expunge(sponsor)  # expunge the object from session
            make_transient(sponsor)
            sponsor.event_id = event.id
            logo_url = create_save_resized_image(image_file=sponsor.logo_url, resize=False)
            delattr(sponsor, 'id')
            sponsor.logo_url = logo_url
            save_to_db(sponsor)

        for location in microlocations:
            location_id = location.id
            db.session.expunge(location)  # expunge the object from session
            make_transient(location)
            location.event_id = event.id
            delattr(location, 'id')
            save_to_db(location)

        # No sessions are copied for new tracks
        for track in tracks:
            track_id = track.id
            db.session.expunge(track)  # expunge the object from session
            make_transient(track)
            track.event_id = event.id
            delattr(track, 'id')
            save_to_db(track)

        for call in speaker_calls:
            call_id = call.id
            db.session.expunge(call)  # expunge the object from session
            make_transient(call)
            call.event_id = event.id
            delattr(call, 'id')
            save_to_db(call)

        for code in discount_codes:
            code_id = code.id
            db.session.expunge(code)  # expunge the object from session
            make_transient(code)
            code.event_id = event.id
            delattr(code, 'id')
            save_to_db(code)

        for form in custom_forms:
            form_id = form.id
            db.session.expunge(form)  # expunge the object from session
            make_transient(form)
            form.event_id = event.id
            delattr(form, 'id')
            save_to_db(form)

        return event
