import json

from app.models.order import Order
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
