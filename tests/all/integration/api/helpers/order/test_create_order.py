import json

from app.api.helpers.db import get_or_create
from app.models.order import Order
from app.models.role import Role
from app.models.ticket_holder import TicketHolder
from app.models.users_events_role import UsersEventsRoles
from tests.factories.attendee import AttendeeFactoryBase
from tests.factories.discount_code import DiscountCodeTicketSubFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.order import OrderSubFactory

from .test_calculate_order_amount import (
    _create_taxed_tickets,
    _create_ticket_dict,
    _create_tickets,
)


def test_create_order(client, db, jwt):
    discount_code = DiscountCodeTicketSubFactory(type='percent', value=10.0, tickets=[])
    tickets_dict = _create_taxed_tickets(
        db, tax_included=False, discount_code=discount_code
    )
    db.session.commit()

    response = client.post(
        '/v1/orders/create-order',
        content_type='application/json',
        headers=jwt,
        data=json.dumps(
            {'tickets': tickets_dict, 'discount-code': str(discount_code.id)}
        ),
    )

    assert TicketHolder.query.count() == 12

    assert response.status_code == 200
    order_dict = json.loads(response.data)
    order = Order.query.get(order_dict['data']['id'])
    assert order_dict['data']['attributes']['amount'] == 4745.81
    assert order.amount == 4745.81
    assert len(order.ticket_holders) == 12
    assert order.discount_code == discount_code


def test_create_order_without_discount(client, db, jwt):
    tickets_dict = _create_taxed_tickets(db, tax_included=False)
    db.session.commit()

    response = client.post(
        '/v1/orders/create-order',
        content_type='application/json',
        headers=jwt,
        data=json.dumps({'tickets': tickets_dict}),
    )

    assert TicketHolder.query.count() == 12

    assert response.status_code == 200
    order_dict = json.loads(response.data)
    order = Order.query.get(order_dict['data']['id'])
    assert order_dict['data']['attributes']['amount'] == 5240.73
    assert order.amount == 5240.73
    ticket_holders = order.ticket_holders
    assert len(ticket_holders) == 12
    assert order.discount_code is None
    for ticket_holder in ticket_holders:
        assert ticket_holder.event_id is not None


def test_create_order_override_amount(client, db, admin_jwt):
    tickets = _create_tickets([10, 20], event=EventFactoryBasic(), quantity=2)
    db.session.commit()

    response = client.post(
        '/v1/orders/create-order',
        content_type='application/json',
        headers=admin_jwt,
        data=json.dumps({'amount': 0, 'tickets': _create_ticket_dict(tickets, [1, 2])}),
    )

    assert response.status_code == 200
    order_dict = json.loads(response.data)
    order = Order.query.get(order_dict['data']['id'])
    assert order_dict['data']['attributes']['amount'] == 0.0
    assert order.amount == 0.0


def test_create_order_override_amount_organizer(client, db, user, jwt):
    event = EventFactoryBasic()
    tickets = _create_tickets([10, 20], event=event, quantity=2)
    role, _ = get_or_create(Role, name='owner', title_name='Owner')
    UsersEventsRoles(user=user, event=event, role=role)
    db.session.commit()

    response = client.post(
        '/v1/orders/create-order',
        content_type='application/json',
        headers=jwt,
        data=json.dumps({'amount': 0, 'tickets': _create_ticket_dict(tickets, [1, 2])}),
    )

    assert response.status_code == 200
    order_dict = json.loads(response.data)
    order = Order.query.get(order_dict['data']['id'])
    assert order_dict['data']['attributes']['amount'] == 0
    assert order.amount == 0


def test_create_order_override_amount_ignore(client, db, jwt):
    # For normal user, amount parameter should be ignored
    tickets = _create_tickets([10, 20], event=EventFactoryBasic(), quantity=2)
    db.session.commit()

    response = client.post(
        '/v1/orders/create-order',
        content_type='application/json',
        headers=jwt,
        data=json.dumps({'amount': 0, 'tickets': _create_ticket_dict(tickets, [1, 2])}),
    )

    assert response.status_code == 200
    order_dict = json.loads(response.data)
    order = Order.query.get(order_dict['data']['id'])
    assert order_dict['data']['attributes']['amount'] == 50.0
    assert order.amount == 50.0


def test_throw_ticket_sold_out(client, db, jwt):
    event = EventFactoryBasic()
    tickets = _create_tickets([10, 20], event=event, quantity=2)
    order = OrderSubFactory(status='completed', event=event)
    AttendeeFactoryBase.create_batch(2, order=order, ticket=tickets[0], event=event)
    AttendeeFactoryBase.create_batch(2, order=order, ticket=tickets[1], event=event)
    db.session.commit()

    response = client.post(
        '/v1/orders/create-order',
        content_type='application/json',
        headers=jwt,
        data=json.dumps(
            {
                'tickets': [
                    {'id': tickets[0].id, 'quantity': 2},
                    {'id': tickets[1].id, 'quantity': 3},
                ]
            }
        ),
    )

    assert TicketHolder.query.count() == 0

    assert response.status_code == 409
    error_dict = json.loads(response.data)
    assert error_dict['errors'][0]['title'] == 'Conflict'
    assert 'already sold out' in error_dict['errors'][0]['detail']


def test_throw_empty_tickets(client, db, jwt):
    response = client.post(
        '/v1/orders/create-order',
        content_type='application/json',
        headers=jwt,
        data=json.dumps({'tickets': []}),
    )

    assert response.status_code == 422
    assert json.loads(response.data) == {
        "errors": [
            {
                "status": 422,
                "source": {"source": "tickets"},
                "title": "Unprocessable Entity",
                "detail": "Tickets missing in Order request",
            }
        ],
        "jsonapi": {"version": "1.0"},
    }


def test_throw_free_tickets(client, db, jwt):
    tickets = _create_tickets([0, 0], event=EventFactoryBasic(), type='free')
    db.session.commit()
    response = client.post(
        '/v1/orders/create-order',
        content_type='application/json',
        headers=jwt,
        data=json.dumps({'tickets': _create_ticket_dict(tickets, [1, 2])}),
    )

    assert response.status_code == 403
    assert json.loads(response.data) == {
        "errors": [
            {
                "status": 403,
                "source": {
                    "pointer": "/data/relationships/user",
                    "code": "unverified-user",
                },
                "title": "Access Forbidden",
                "detail": "Unverified user cannot place free orders",
            }
        ],
        "jsonapi": {"version": "1.0"},
    }
