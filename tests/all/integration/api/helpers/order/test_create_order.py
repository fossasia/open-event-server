import json

import pytest

from tests.factories.discount_code import DiscountCodeTicketSubFactory
from .test_calculate_order_amount import _create_taxed_tickets, _create_tickets
from tests.factories.user import UserFactory
from flask_jwt_extended.utils import create_access_token
from app.models.ticket_holder import TicketHolder
from tests.factories.event import EventFactoryBasic
from tests.factories.order import OrderFactory, OrderSubFactory
from tests.factories.attendee import AttendeeFactoryBase


@pytest.fixture
def jwt(db):
    user = UserFactory()
    db.session.commit()

    return {'Authorization': "JWT " + create_access_token(user.id, fresh=True)}


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
    amount_data = json.loads(response.data)
    assert amount_data['sub_total'] == 4021.87
    assert amount_data['total'] == 4745.81
    assert amount_data['tax']['included'] is False
    assert amount_data['tax']['amount'] == 723.94


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
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': 'Ticket 5 already sold out',
                'source': {'id': 5},
                'status': 409,
                'title': 'Conflict',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }


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
