from datetime import datetime

import pytest
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.db import (
    get_count,
    get_or_create,
    safe_query,
    safe_query_by_id,
    save_to_db,
)
from app.models.event import Event
from app.models.ticket_holder import TicketHolder
from tests.factories.attendee import AttendeeSubFactory
from tests.factories.event import EventFactoryBasic


def test_save_to_db(db):
    """Method to test the function save_to_db"""

    obj = EventFactoryBasic()
    save_to_db(obj)
    event = Event.query.filter_by(id=obj.id).first()
    assert event.id == obj.id
    assert event == obj


def test_safe_query(db):
    """Method to test the function safe_query"""

    event = EventFactoryBasic()
    save_to_db(event)
    obj = safe_query(Event, 'id', event.id, 'event_id')
    assert event.id == obj.id
    assert event == obj


def test_safe_query_exception(db):
    """Method to test the exception in function safe_query"""

    with pytest.raises(ObjectNotFound):
        safe_query_by_id(Event, 1)


def test_get_or_create(db):
    """Method to test the function get_or_create"""

    event = EventFactoryBasic()
    save_to_db(event)
    obj, is_created = get_or_create(Event, name=event.name)
    assert event.id == obj.id
    assert is_created is False

    obj, is_created = get_or_create(
        Event, name="new event", starts_at=event.starts_at, ends_at=event.ends_at
    )
    assert event.id != obj.id
    assert is_created is True


def test_get_count(db):
    """Method to test the number of queries concerning a Model"""

    attendee = AttendeeSubFactory()
    save_to_db(attendee)
    assert get_count(TicketHolder.query) == 1


def test_filter_deleted_event(db):
    event = EventFactoryBasic(deleted_at=datetime.now())
    db.session.commit()

    with pytest.raises(ObjectNotFound):
        safe_query(Event, 'id', event.id, 'id')


def test_allow_deleted_event_for_admin(db, app):
    obj = EventFactoryBasic(deleted_at=datetime.now())
    db.session.commit()

    with app.test_request_context('?get_trashed=true'):
        event = safe_query(Event, 'id', obj.id, 'id')
        assert event.id == obj.id
        assert event == obj
