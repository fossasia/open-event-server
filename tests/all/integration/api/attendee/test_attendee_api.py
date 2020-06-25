import json

from app.models.custom_form import CustomForms
from tests.factories.attendee import AttendeeOrderTicketSubFactory
from tests.factories.order import OrderSubFactory
from tests.factories.ticket import TicketSubFactory


def get_minimal_attendee(db):
    attendee = AttendeeOrderTicketSubFactory(
        email=None, address=None, city=None, state=None, country=None
    )
    db.session.commit()

    return attendee


def test_edit_attendee_minimum_fields(db, client, jwt):
    attendee = get_minimal_attendee(db)

    data = json.dumps(
        {
            'data': {
                'type': 'attendee',
                'id': str(attendee.id),
                "attributes": {"firstname": "Areeb", "lastname": "Jamal"},
            }
        }
    )

    client.patch(
        f'/v1/attendees/{attendee.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(attendee)

    assert attendee.firstname == 'Areeb'
    assert attendee.lastname == 'Jamal'


def get_simple_custom_form_attendee(db):
    attendee = get_minimal_attendee(db)
    CustomForms(
        event=attendee.event,
        form='attendee',
        field_identifier='email',
        type='text',
        is_included=True,
        is_required=True,
    )
    CustomForms(
        event=attendee.event,
        form='attendee',
        field_identifier='taxBusinessInfo',
        type='text',
        is_included=True,
        is_required=True,
    )
    db.session.commit()

    return attendee


def test_edit_attendee_required_fields_missing(db, client, jwt):
    attendee = get_simple_custom_form_attendee(db)

    data = json.dumps(
        {
            'data': {
                'type': 'attendee',
                'id': str(attendee.id),
                "attributes": {
                    "firstname": "Areeb",
                    "lastname": "Jamal",
                    "city": "hello@world.com",
                },
            }
        }
    )

    response = client.patch(
        f'/v1/attendees/{attendee.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(attendee)

    assert response.status_code == 422
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Missing required fields ['email', 'tax_business_info']",
                'source': {'pointer': '/data/attributes'},
                'status': 422,
                'title': 'Unprocessable Entity',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }

    assert attendee.firstname != 'Areeb'
    assert attendee.lastname != 'Jamal'
    assert attendee.email is None


def test_edit_attendee_required_fields_complete(db, client, jwt):
    attendee = get_simple_custom_form_attendee(db)

    data = json.dumps(
        {
            'data': {
                'type': 'attendee',
                'id': str(attendee.id),
                "attributes": {
                    "firstname": "Areeb",
                    "lastname": "Jamal",
                    "email": "test@test.org",
                    "tax_business_info": "Hello",
                },
            }
        }
    )

    response = client.patch(
        f'/v1/attendees/{attendee.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(attendee)

    assert response.status_code == 200

    assert attendee.firstname == 'Areeb'
    assert attendee.lastname == 'Jamal'
    assert attendee.email == 'test@test.org'
    assert attendee.tax_business_info == 'Hello'


def get_complex_custom_form_attendee(db):
    attendee = get_minimal_attendee(db)
    CustomForms(
        event=attendee.event,
        form='attendee',
        field_identifier='jobTitle',
        type='text',
        is_included=True,
        is_required=True,
    )
    CustomForms(
        event=attendee.event,
        form='attendee',
        field_identifier='bestFriend',
        name='Best Friend',
        type='text',
        is_included=True,
        is_required=True,
        is_complex=True,
    )
    db.session.commit()

    return attendee


def test_custom_form_complex_fields_missing_required(db, client, jwt):
    attendee = get_complex_custom_form_attendee(db)

    data = json.dumps(
        {
            'data': {
                'type': 'attendee',
                'id': str(attendee.id),
                "attributes": {"firstname": "Areeb", "lastname": "Jamal"},
            }
        }
    )

    response = client.patch(
        f'/v1/attendees/{attendee.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(attendee)

    assert response.status_code == 422
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Missing required fields ['best_friend', 'job_title']",
                'source': {'pointer': '/data/attributes'},
                'status': 422,
                'title': 'Unprocessable Entity',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }

    assert attendee.firstname != 'Areeb'
    assert attendee.lastname != 'Jamal'
    assert attendee.complex_field_values is None


def test_custom_form_complex_fields_missing_required_one(db, client, jwt):
    attendee = get_complex_custom_form_attendee(db)

    data = json.dumps(
        {
            'data': {
                'type': 'attendee',
                'id': str(attendee.id),
                "attributes": {
                    "firstname": "Areeb",
                    "lastname": "Jamal",
                    "job_title": "Software Engineer",
                    "complex-field-values": {"favourite-friend": "Tester"},
                },
            }
        }
    )

    response = client.patch(
        f'/v1/attendees/{attendee.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(attendee)

    assert response.status_code == 422
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Missing required fields ['best_friend']",
                'source': {'pointer': '/data/attributes'},
                'status': 422,
                'title': 'Unprocessable Entity',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }

    assert attendee.firstname != 'Areeb'
    assert attendee.lastname != 'Jamal'
    assert attendee.complex_field_values is None


def test_custom_form_complex_fields_complete(db, client, jwt):
    attendee = get_complex_custom_form_attendee(db)

    data = json.dumps(
        {
            'data': {
                'type': 'attendee',
                'id': str(attendee.id),
                "attributes": {
                    "firstname": "Areeb",
                    "lastname": "Jamal",
                    "job-title": "Software Engineer",
                    "complex-field-values": {"best-friend": "Tester"},
                },
            }
        }
    )

    response = client.patch(
        f'/v1/attendees/{attendee.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(attendee)

    assert response.status_code == 200

    assert attendee.firstname == 'Areeb'
    assert attendee.lastname == 'Jamal'
    assert attendee.job_title == 'Software Engineer'
    assert attendee.complex_field_values['best_friend'] == 'Tester'


def test_edit_attendee_ticket(db, client, jwt):
    attendee = AttendeeOrderTicketSubFactory()
    ticket = TicketSubFactory(event=attendee.event)
    db.session.commit()

    attendee_ticket = attendee.ticket

    data = json.dumps(
        {
            'data': {
                'type': 'attendee',
                'id': str(attendee.id),
                "relationships": {
                    "ticket": {"data": {"id": str(ticket.id), "type": "ticket"}}
                },
            }
        }
    )

    client.patch(
        f'/v1/attendees/{attendee.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(attendee)

    # Ticket should not be updated
    assert attendee.ticket.id != ticket.id
    assert attendee.ticket.id == attendee_ticket.id


def test_edit_attendee_order(db, client, jwt):
    attendee = AttendeeOrderTicketSubFactory()
    order = OrderSubFactory(event=attendee.event)
    db.session.commit()

    attendee_order = attendee.order

    data = json.dumps(
        {
            'data': {
                'type': 'attendee',
                'id': str(attendee.id),
                "relationships": {
                    "order": {"data": {"id": str(order.id), "type": "order"}}
                },
            }
        }
    )

    client.patch(
        f'/v1/attendees/{attendee.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(attendee)

    # Order should not be updated
    assert attendee.order.id != order.id
    assert attendee.order.id == attendee_order.id
