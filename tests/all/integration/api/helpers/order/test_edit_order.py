import json

from app.models.order import Order
from app.models.custom_form import CustomForms
from app.models.ticket_holder import TicketHolder
from tests.factories.attendee import AttendeeSubFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.order import OrderSubFactory


def create_order(db, user):
    order = OrderSubFactory(amount=234, status='initializing', user=user)
    AttendeeSubFactory.create_batch(3, order=order)
    db.session.commit()

    return str(order.id)


def test_throw_on_order_amount_update(client, db, user, jwt):
    order_id = create_order(db, user)

    response = client.patch(
        f'/v1/orders/{order_id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=json.dumps(
            {'data': {'attributes': {'amount': 10}, 'type': 'order', 'id': order_id}}
        ),
    )

    assert response.status_code == 403
    assert (
        json.loads(response.data)['errors'][0]['detail']
        == 'You cannot update amount of an order'
    )


def test_ignore_on_order_attendee_update(client, db, user, jwt):
    order_id = create_order(db, user)
    attendee = AttendeeSubFactory()
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'order',
                'id': order_id,
                "relationships": {
                    "attendees": {"data": [{"id": str(attendee.id), "type": "attendee"}]}
                },
            }
        }
    )

    response = client.patch(
        f'/v1/orders/{order_id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    order = Order.query.get(order_id)
    assert response.status_code == 200
    assert len(order.ticket_holders) == 3


def test_ignore_on_order_event_update(client, db, user, jwt):
    order_id = create_order(db, user)
    order = Order.query.get(order_id)
    order_event = order.event
    event = EventFactoryBasic()
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'order',
                'id': order_id,
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}}
                },
            }
        }
    )

    response = client.patch(
        f'/v1/orders/{order_id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(order)
    assert response.status_code == 200
    assert order.event == order_event


def get_complex_custom_form_order(db, user):
    order = OrderSubFactory(amount=234, status='initializing', user=user)
    attendee = AttendeeSubFactory(order=order)

    CustomForms(
        event=attendee.event,
        form='attendee',
        field_identifier='whatUniversity',
        name='what university',
        type='text',
        is_complex=True,
        is_included=True,
        is_required=True,
    )

    CustomForms(
        event=attendee.event,
        form='attendee',
        field_identifier='whatCollege',
        name='what college',
        type='text',
        is_complex=True,
        is_included=True,
        is_required=True,
    )

    CustomForms(
        event=attendee.event,
        form='attendee',
        field_identifier='naamBatao',
        name='naam batao',
        type='text',
        is_complex=True,
        is_included=True,
        is_required=False,
    )

    db.session.commit()

    return str(order.id)


def test_order_pending_incomplete_complex_custom_form(client, db, user, jwt):
    order_id = get_complex_custom_form_order(db, user)
    order = Order.query.get(order_id)

    data = json.dumps(
        {
            "data": {
                "attributes": {"status": "pending", "order-notes": "do it pending"},
                "type": "order",
                "id": order_id,
            }
        }
    )

    response = client.patch(
        f'/v1/orders/{order_id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(order)

    assert response.status_code == 422
    assert order.status != "pending"
    assert order.order_notes != "do it pending"
    assert json.loads(response.data) == {
        'errors': [
            {
                'status': 422,
                'source': {'pointer': '/data/attributes'},
                'title': 'Unprocessable Entity',
                'detail': "Missing required fields ['what_college', 'what_university']",
            }
        ],
        'jsonapi': {'version': '1.0'},
    }


def test_order_placed_incomplete_complex_custom_form(client, db, user, jwt):
    order_id = get_complex_custom_form_order(db, user)
    order = Order.query.get(order_id)

    data = json.dumps(
        {
            "data": {
                "attributes": {"status": "placed", "order-notes": "just place it"},
                "type": "order",
                "id": order_id,
            }
        }
    )

    response = client.patch(
        f'/v1/orders/{order_id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(order)

    assert response.status_code == 422
    assert order.status != "placed"
    assert order.order_notes != "just place it"
    assert json.loads(response.data) == {
        'errors': [
            {
                'status': 422,
                'source': {'pointer': '/data/attributes'},
                'title': 'Unprocessable Entity',
                'detail': "Missing required fields ['what_college', 'what_university']",
            }
        ],
        'jsonapi': {'version': '1.0'},
    }


def test_order_pending_complete_complex_custom_form(client, db, user, jwt):
    order_id = get_complex_custom_form_order(db, user)
    order = Order.query.get(order_id)

    attendee = TicketHolder.query.filter_by(order_id=order.id).first()
    attendee.complex_field_values = {
        "what_college": "Zakir Hussain College",
        "what_university": "Aligarh Muslim University",
    }
    db.session.commit()

    data = json.dumps(
        {
            "data": {
                "attributes": {"status": "pending", "order-notes": "do it pending"},
                "type": "order",
                "id": order_id,
            }
        }
    )

    response = client.patch(
        f'/v1/orders/{order_id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(order)

    json_response = json.loads(response.data)

    assert response.status_code == 200
    assert order.status == "pending"
    assert order.order_notes == "do it pending"
    assert json_response['data']['attributes']['status'] == "pending"
    assert json_response['data']['attributes']['order-notes'] == "do it pending"
