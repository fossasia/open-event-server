import json

from tests.factories.ticket import TicketSubFactory


def test_ticket_sales_end(db, client, admin_jwt):
    ticket = TicketSubFactory()
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'ticket',
                'id': str(ticket.id),
                "attributes": {"sales-ends-at": "2199-10-01T1:00:00+00:00"},
            }
        }
    )

    response = client.patch(
        f'/v1/tickets/{ticket.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
        data=data,
    )

    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "End of ticket sales date of 'example' cannot be after "
                'end of event date',
                'source': {'sales_ends_at': '/data/attributes/sales-ends-at'},
                'status': 422,
                'title': 'Unprocessable Entity',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }
    assert response.status_code == 422


def test_ticket_has_sales(db, client, admin_jwt):
    ticket = TicketSubFactory()
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'ticket',
                'id': str(ticket.id),
                "has-current-orders": True,
                "attributes": {"deleted-at": "2020-10-01T1:00:00+00:00"},
            }
        }
    )

    response = client.patch(
        f'/v1/tickets/{ticket.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
        data=data,
    )

    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Can't delete a ticket that has sales",
                'source': {'param': 'ticket_id'},
                'status': 403,
                'title': 'Forbidden',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }
    assert response.status_code == 403
