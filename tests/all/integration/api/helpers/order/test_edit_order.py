import json

from app.models.order import Order
from tests.factories.discount_code import DiscountCodeTicketSubFactory

from .test_calculate_order_amount import _create_taxed_tickets
from tests.factories.attendee import AttendeeSubFactory


def create_order(db, client, jwt):
    tickets_dict = _create_taxed_tickets(db)
    db.session.commit()

    response = client.post(
        '/v1/orders/create-order',
        content_type='application/json',
        headers=jwt,
        data=json.dumps({'tickets': tickets_dict}),
    )

    order_dict = json.loads(response.data)
    order_id = order_dict['data']['id']

    return order_id


def test_throw_on_order_amount_update(client, db, jwt):
    order_id = create_order(db, client, jwt)

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


def test_throw_on_order_attendee_update(client, db, jwt):
    order_id = create_order(db, client, jwt)
    attendee = AttendeeSubFactory()
    db.session.commit()

    data=json.dumps(
            {'data': {'type': 'order', 'id': order_id,
            "relationships": {
      "attendees": {
        "data": [
          {
            "id": str(attendee.id),
            "type": "attendee"
          }
        ]
      }
    }}}
        )
    
    response = client.patch(
        f'/v1/orders/{order_id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    print(response.data)
    order = Order.query.get(order_id)
    # assert response.status_code == 403
    assert response.data == ''
    assert len(order.ticket_holders) == 12
