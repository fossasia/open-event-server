from sqlalchemy.orm import make_transient

from app.helpers.data import save_to_db
from app.helpers.data_getter import DataGetter
from app.models import db


def clone_row(row, event_id=None):
    db.session.expunge(row)
    make_transient(row)
    row.id = None
    if event_id:
        row.event_id = event_id
    save_to_db(row)
    db.session.flush()
    return row


def create_event_copy(event_id):
    old_event = DataGetter.get_event(event_id)
    event = clone_row(old_event)
    event.name = "Copy of " + event.name
    event.state = "Draft"
    save_to_db(event)

    sponsors_old = DataGetter.get_sponsors(event_id).all()
    tracks_old = DataGetter.get_tracks(event_id).all()
    microlocations_old = DataGetter.get_microlocations(event_id).all()
    call_for_paper_old = DataGetter.get_call_for_papers(event_id).first()
    social_links = DataGetter.get_social_links_by_event_id(event_id).all()
    custom_forms = DataGetter.get_custom_form_elements(event_id)

    for social_link in social_links:
        clone_row(social_link, event.id)

    for sponsor in sponsors_old:
        clone_row(sponsor, event.id)

    for track in tracks_old:
        clone_row(track, event.id)

    for microlocation in microlocations_old:
        clone_row(microlocation, event.id)

    if call_for_paper_old:
        clone_row(call_for_paper_old, event.id)

    if custom_forms:
        clone_row(custom_forms, event.id)

    return event
