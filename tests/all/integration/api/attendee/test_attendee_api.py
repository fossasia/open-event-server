import json

from app.models.custom_form import CustomForms
from tests.factories.attendee import AttendeeOrderTicketSubFactory
from tests.factories.order import OrderSubFactory
from tests.factories.ticket import TicketSubFactory


def get_minimal_attendee(db, user):
    attendee = AttendeeOrderTicketSubFactory(
        email=None, address=None, city=None, state=None, country=None, order__user=user
    )
    db.session.commit()

    return attendee


def test_edit_attendee_minimum_fields(db, client, jwt, user):
    attendee = get_minimal_attendee(db, user)

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


def get_simple_custom_form_attendee(db, user):
    attendee = get_minimal_attendee(db, user)
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


def test_edit_attendee_required_fields_missing(db, client, jwt, user):
    attendee = get_simple_custom_form_attendee(db, user)

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
                'detail': "Missing required fields ['Email', 'Tax Business Info']",
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


def test_edit_attendee_required_fields_complete(db, client, jwt, user):
    attendee = get_simple_custom_form_attendee(db, user)

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
                    "complex-field-values": {
                        "ko": "mo"
                    },  # Should be ignored and saved as None
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
    assert attendee.complex_field_values is None


def get_complex_custom_form_attendee(db, user):
    attendee = get_minimal_attendee(db, user)
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
    CustomForms(
        event=attendee.event,
        form='attendee',
        field_identifier='transFatContent',
        name='Trans Fat Content',
        type='number',
        is_included=True,
        is_required=False,
        is_complex=True,
    )
    db.session.commit()

    return attendee


def test_custom_form_complex_fields_missing_required(db, client, jwt, user):
    attendee = get_complex_custom_form_attendee(db, user)

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
                'detail': "Missing required fields ['Best Friend', 'Job Title']",
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


def test_custom_form_complex_fields_missing_form_disabled(db, client, jwt, user):
    attendee = get_complex_custom_form_attendee(db, user)
    attendee.event.is_ticket_form_enabled = False
    db.session.commit()

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

    assert response.status_code == 200

    assert attendee.firstname == 'Areeb'
    assert attendee.lastname == 'Jamal'
    assert attendee.job_title == 'Software Engineer'
    assert attendee.complex_field_values is None


def test_custom_form_complex_fields_missing_required_one(db, client, jwt, user):
    attendee = get_complex_custom_form_attendee(db, user)

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
                'detail': "Missing required fields ['Best Friend']",
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


def test_custom_form_complex_fields_complete(db, client, jwt, user):
    attendee = get_complex_custom_form_attendee(db, user)

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


def test_ignore_complex_custom_form_fields(db, client, jwt, user):
    """Test to see that extra data from complex JSON is dropped"""
    attendee = get_complex_custom_form_attendee(db, user)

    data = json.dumps(
        {
            'data': {
                'type': 'attendee',
                'id': str(attendee.id),
                "attributes": {
                    "firstname": "Areeb",
                    "lastname": "Jamal",
                    "job-title": "Software Engineer",
                    "complex-field-values": {
                        "bestFriend": "Bester",
                        "transFat-content": 20.08,
                        "shalimar": "sophie",
                    },
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
    assert attendee.complex_field_values['best_friend'] == 'Bester'
    assert attendee.complex_field_values['trans_fat_content'] == 20.08
    assert attendee.complex_field_values.get('shalimar') is None


def test_throw_complex_custom_form_fields(db, client, jwt, user):
    attendee = get_complex_custom_form_attendee(db, user)
    CustomForms(
        event=attendee.event,
        form='attendee',
        field_identifier='secondaryEmail',
        name='Secondary Email',
        type='email',
        is_included=True,
        is_required=False,
        is_complex=True,
    )
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'attendee',
                'id': str(attendee.id),
                "attributes": {
                    "firstname": "Areeb",
                    "lastname": "Jamal",
                    "job-title": "Software Engineer",
                    "complex-field-values": {
                        "bestFriend": "Bester",
                        "secondary-email": "notanemail.com",
                    },
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
        "errors": [
            {
                "status": 422,
                "source": {"errors": {"secondary_email": ["Not a valid email address."]}},
                "title": "Unprocessable Entity",
                "detail": "Schema Validation Error",
            }
        ],
        "jsonapi": {"version": "1.0"},
    }


def test_throw_invalid_complex_custom_form_fields(db, client, jwt, user):
    attendee = get_complex_custom_form_attendee(db, user)
    CustomForms(
        event=attendee.event,
        form='attendee',
        field_identifier='genderFile',
        name='Gender File',
        type='file',
        is_included=True,
        is_required=False,
        is_complex=True,
    )
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'attendee',
                'id': str(attendee.id),
                "attributes": {
                    "firstname": "Areeb",
                    "lastname": "Jamal",
                    "job-title": "Software Engineer",
                    "complex-field-values": {
                        "bestFriend": "Bester",
                        "gender-file": "notanemail.com",
                    },
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
                'detail': 'Invalid Field Type: file',
                'source': {'pointer': '/data/complex-field-values/gender_file'},
                'status': 422,
                'title': 'Unprocessable Entity',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }


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


def test_edit_attendee_when_order_is_pending(db, client, jwt, user):
    attendee = AttendeeOrderTicketSubFactory(order__user=user)
    order = attendee.order

    order.status = "pending"

    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'attendee',
                'id': str(attendee.id),
                'attributes': {"lastname": "Ali"},
                "relationships": {
                    "order": {"data": {"id": str(order.id), "type": "order"}}
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

    # Attendee should not be updated
    assert response.status_code == 422
    assert attendee.lastname != "Ali"


def test_edit_attendee_when_order_is_completed(db, client, jwt, user):
    attendee = AttendeeOrderTicketSubFactory(order__user=user)
    order = attendee.order

    order.status = "completed"

    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'attendee',
                'id': str(attendee.id),
                'attributes': {"firstname": "Haider"},
                "relationships": {
                    "order": {"data": {"id": str(order.id), "type": "order"}}
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

    # Attendee should not be updated
    assert response.status_code == 422
    assert attendee.firstname != "Haider"


def test_edit_attendee_by_some_other_user(db, client, jwt):
    attendee = AttendeeOrderTicketSubFactory()
    order = attendee.order

    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'attendee',
                'id': str(attendee.id),
                'attributes': {"firstname": "Haider"},
                "relationships": {
                    "order": {"data": {"id": str(order.id), "type": "order"}}
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

    assert response.status_code == 403

    assert attendee.firstname != "Haider"

    assert json.loads(response.data) == {
        'errors': [
            {
                'status': 403,
                'source': None,
                'title': 'Access Forbidden',
                'detail': 'Only admin or that user itself can update attendee info',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }
