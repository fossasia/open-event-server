from datetime import datetime

import pytest
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.errors import ConflictError
from app.api.helpers.ticketing import validate_ticket_holders
from tests.factories.attendee import AttendeeSubFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.order import OrderSubFactory


def test_validate_ticket_holders(db):
    attendees = AttendeeSubFactory.create_batch(3, event=EventFactoryBasic())
    db.session.commit()

    assert attendees == validate_ticket_holders([str(att.id) for att in attendees])


def test_reject_attendees_with_order(db):
    attendees = AttendeeSubFactory.create_batch(2)
    attendees.append(AttendeeSubFactory(order=OrderSubFactory()))
    db.session.commit()

    with pytest.raises(
        ConflictError,
        match=f'Order already exists for attendee with id {attendees[-1].id}',
    ):
        validate_ticket_holders([att.id for att in attendees])


def test_reject_deleted_attendees(db):
    attendees = AttendeeSubFactory.create_batch(3)
    attendees += AttendeeSubFactory.create_batch(2, deleted_at=datetime.now())
    db.session.commit()

    with pytest.raises(ObjectNotFound, match='Some attendee among ids .* do not exist'):
        validate_ticket_holders([att.id for att in attendees])
