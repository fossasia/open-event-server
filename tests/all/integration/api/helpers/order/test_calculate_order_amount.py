import json
from datetime import datetime

import pytest
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.errors import UnprocessableEntityError
from app.api.helpers.order import calculate_order_amount
from tests.factories.discount_code import DiscountCodeTicketSubFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.tax import TaxSubFactory
from tests.factories.ticket import TicketSubFactory


def test_no_amount(db):
    amount_data = calculate_order_amount([])

    assert amount_data['total'] == 0.0
    assert amount_data['tax'] is None
    assert amount_data['discount'] == 0.0
    assert amount_data['tickets'] == []


def test_single_ticket(db):
    ticket = TicketSubFactory(price=10)
    db.session.commit()

    amount_data = calculate_order_amount([{'id': ticket.id}])

    assert amount_data['total'] == 10.0
    assert amount_data['tax'] is None
    assert amount_data['discount'] == 0.0
    ticket_dict = amount_data['tickets'][0]
    assert ticket_dict['id'] == ticket.id
    assert ticket_dict['name'] == ticket.name
    assert ticket_dict['price'] == ticket.price
    assert ticket_dict['quantity'] == 1
    assert ticket_dict['ticket_fee'] == 0.0
    assert ticket_dict['sub_total'] == 10.0


def _create_ticket_dict(tickets, quantities):
    return [
        dict(id=ticket.id, quantity=quantity)
        for ticket, quantity in zip(tickets, quantities)
    ]


def test_multiple_tickets_different_event(db):
    ticket1 = TicketSubFactory()
    ticket2 = TicketSubFactory()

    db.session.commit()

    ticket_dict = _create_ticket_dict([ticket1, ticket2], [1, 2])

    with pytest.raises(
        UnprocessableEntityError, match=r".*All tickets must belong to same event.*"
    ):
        calculate_order_amount(ticket_dict)


def test_multiple_tickets(db):
    ticket = TicketSubFactory(price=50)
    ticket2 = TicketSubFactory(price=12.5, event=ticket.event)
    ticket3 = TicketSubFactory(price=233.15, event=ticket.event)
    db.session.commit()

    tickets = _create_ticket_dict([ticket3, ticket2, ticket], [2, 1, 3])

    amount_data = calculate_order_amount(tickets)

    assert amount_data['total'] == 628.8
    assert amount_data['tax'] is None
    assert amount_data['discount'] == 0.0
    ticket_dict = amount_data['tickets'][0]
    assert ticket_dict['id'] == ticket.id
    assert ticket_dict['name'] == ticket.name
    assert ticket_dict['price'] == ticket.price
    assert ticket_dict['quantity'] == 3
    assert ticket_dict['ticket_fee'] == 0.0
    assert ticket_dict['sub_total'] == 150.0
    assert amount_data['tickets'][-1]['id'] == ticket3.id
    assert amount_data['tickets'][-1]['price'] == ticket3.price
    assert amount_data['tickets'][-1]['quantity'] == 2
    assert amount_data['tickets'][-1]['sub_total'] == 466.3


def _create_tickets(prices, **kwargs):
    return [TicketSubFactory(price=price, **kwargs) for price in prices]


def _create_donation_tickets(db):
    event = EventFactoryBasic()
    tickets = _create_tickets([10, 20], event=event)
    tickets.append(
        TicketSubFactory(type='donation', max_price=20, min_price=10, event=event)
    )
    db.session.commit()

    return _create_ticket_dict(tickets[::-1], [2, 1, 3])


def _expect_donation_error(ticket_dict):
    with pytest.raises(
        UnprocessableEntityError,
        match='Price for donation ticket should be present and within range '
        '10.0 to 20.0',
    ):
        calculate_order_amount(ticket_dict)


def test_donation_ticket_without_price(db):
    ticket_dict = _create_donation_tickets(db)
    _expect_donation_error(ticket_dict)


def test_donation_ticket_with_lower_price(db):
    ticket_dict = _create_donation_tickets(db)
    ticket_dict[-1]['price'] = 5.0

    _expect_donation_error(ticket_dict)


def test_donation_ticket_with_higher_price(db):
    ticket_dict = _create_donation_tickets(db)
    ticket_dict[-1]['price'] = 25.0

    _expect_donation_error(ticket_dict)


def test_donation_ticket(db):
    ticket_dict = _create_donation_tickets(db)
    ticket_dict[0]['price'] = 15.13

    amount_data = calculate_order_amount(ticket_dict)

    assert amount_data['total'] == 80.26
    assert amount_data['tax'] is None
    assert amount_data['discount'] == 0.0
    ticket_dict = amount_data['tickets'][0]
    assert ticket_dict['price'] == 10
    assert ticket_dict['quantity'] == 3
    assert ticket_dict['sub_total'] == 30.0
    assert amount_data['tickets'][-1]['price'] == 15.13
    assert amount_data['tickets'][-1]['quantity'] == 2
    assert amount_data['tickets'][-1]['sub_total'] == 30.26


def _create_taxed_tickets(db, tax_included=True, discount_code=None):
    tax = TaxSubFactory(name='GST', rate=18.0, is_tax_included_in_price=tax_included)
    tickets = _create_tickets([123.5, 456.3], event=tax.event)
    tickets += [
        TicketSubFactory(
            type='donation', event=tax.event, min_price=500.0, max_price=1000.0
        ),
        TicketSubFactory(type='free', price=435.0, event=tax.event),
    ]

    if discount_code:
        discount_code.tickets = [tickets[1]] + tickets[2:]

    db.session.commit()

    tickets_dict = _create_ticket_dict(tickets, [2, 4, 3, 3])
    # Set price of donation ticket
    tickets_dict[-2]['price'] = 789.7

    return tickets_dict


def test_tax_included(db):
    tickets_dict = _create_taxed_tickets(db)

    amount_data = calculate_order_amount(tickets_dict)

    assert amount_data['sub_total'] == 4441.3
    assert amount_data['total'] == 4441.3
    assert amount_data['tax']['included'] is True
    assert amount_data['tax']['percent'] == 18.0
    assert amount_data['tax']['amount'] == 677.49
    assert amount_data['tax']['name'] == 'GST'
    assert amount_data['discount'] == 0.0


def test_tax_excluded(db):
    tickets_dict = _create_taxed_tickets(db, tax_included=False)

    amount_data = calculate_order_amount(tickets_dict)

    assert amount_data['sub_total'] == 4441.3
    assert amount_data['total'] == pytest.approx(4441.3 + 799.43)
    assert amount_data['tax']['included'] is False
    assert amount_data['tax']['percent'] == 18.0
    assert amount_data['tax']['amount'] == 799.43
    assert amount_data['tax']['name'] == 'GST'
    assert amount_data['discount'] == 0.0


def test_discount_code(db):
    ticket = TicketSubFactory(price=100.0)
    discount_code = DiscountCodeTicketSubFactory(
        type='percent', value=10.0, tickets=[ticket]
    )
    db.session.commit()

    amount_data = calculate_order_amount(
        [{'id': ticket.id}], discount_code=discount_code.id
    )

    assert amount_data['total'] == 90.0
    assert amount_data['tax'] is None
    assert amount_data['discount'] == 10.0
    ticket_dict = amount_data['tickets'][0]
    assert ticket_dict['id'] == ticket.id
    assert ticket_dict['name'] == ticket.name
    assert ticket_dict['price'] == ticket.price
    assert ticket_dict['quantity'] == 1
    assert ticket_dict['ticket_fee'] == 0.0
    assert ticket_dict['sub_total'] == 90.0
    assert ticket_dict['discount']['total'] == 10.0
    assert ticket_dict['discount']['amount'] == 10.0
    assert ticket_dict['discount']['percent'] == 10.0
    assert ticket_dict['discount']['code'] == discount_code.code


def test_no_amount_with_discount(db):
    ticket = TicketSubFactory(price=100.0)
    discount_code = DiscountCodeTicketSubFactory(
        type='percent', value=10.0, tickets=[ticket]
    )
    db.session.commit()

    amount_data = calculate_order_amount([], discount_code.id)

    assert amount_data['total'] == 0.0
    assert amount_data['tax'] is None
    assert amount_data['discount'] == 0.0
    assert amount_data['tickets'] == []


def test_multiple_tickets_discount(db):
    ticket_a = TicketSubFactory(price=50.0)
    ticket_b = TicketSubFactory(price=495.8, event=ticket_a.event)
    ticket_c = TicketSubFactory(price=321.3, event=ticket_a.event)
    # Deliberately add price to free ticket
    ticket_d = TicketSubFactory(price=500.0, event=ticket_a.event, type='free')

    discount = DiscountCodeTicketSubFactory(
        type='percent', value=50.0, tickets=[ticket_a, ticket_b]
    )
    DiscountCodeTicketSubFactory(type='amount', value=100.0, tickets=[ticket_c])

    db.session.commit()

    tickets_dict = _create_ticket_dict(
        [ticket_a, ticket_b, ticket_c, ticket_d], [2, 3, 1, 2]
    )

    amount_data = calculate_order_amount(tickets_dict, discount_code=discount.id)

    assert amount_data['total'] == 1115.0
    assert amount_data['discount'] == 793.7
    assert amount_data['tickets'][0]['quantity'] == 2
    assert amount_data['tickets'][0]['price'] == 50.0
    assert amount_data['tickets'][0]['sub_total'] == 50.0
    assert amount_data['tickets'][0]['discount']['total'] == 50.0
    assert amount_data['tickets'][0]['discount']['amount'] == 25.0
    assert amount_data['tickets'][0]['discount']['percent'] == 50.0
    assert amount_data['tickets'][1]['quantity'] == 3
    assert amount_data['tickets'][1]['price'] == 495.8
    assert amount_data['tickets'][1]['sub_total'] == 743.7
    assert amount_data['tickets'][1]['discount']['total'] == 743.7
    assert amount_data['tickets'][1]['discount']['amount'] == 247.9
    assert amount_data['tickets'][1]['discount']['percent'] == 50.0
    assert amount_data['tickets'][2]['quantity'] == 1
    assert amount_data['tickets'][2]['price'] == 321.3
    assert amount_data['tickets'][2]['sub_total'] == 321.3
    assert amount_data['tickets'][2]['discount'] is None


def test_discount_code_amount_type(db):
    ticket = TicketSubFactory(price=100.0)
    discount_code = DiscountCodeTicketSubFactory(
        type='amount', value=50.0, tickets=[ticket]
    )
    db.session.commit()

    amount_data = calculate_order_amount(
        [{'id': ticket.id}], discount_code=discount_code.id
    )

    assert amount_data['total'] == 50.0
    assert amount_data['discount'] == 50.0
    ticket_dict = amount_data['tickets'][0]
    assert ticket_dict['sub_total'] == 50.0
    assert ticket_dict['discount']['total'] == 50.0
    assert ticket_dict['discount']['amount'] == 50.0
    assert ticket_dict['discount']['percent'] == 50.0
    assert ticket_dict['discount']['code'] == discount_code.code


def test_discount_code_more_amount(db):
    ticket = TicketSubFactory(price=50.0)
    discount_code = DiscountCodeTicketSubFactory(
        type='amount', value=100.0, tickets=[ticket]
    )
    db.session.commit()

    amount_data = calculate_order_amount(
        [{'id': ticket.id}], discount_code=discount_code.id
    )

    assert amount_data['total'] == 0.0
    assert amount_data['discount'] == 50.0
    ticket_dict = amount_data['tickets'][0]
    assert ticket_dict['id'] == ticket.id
    assert ticket_dict['name'] == ticket.name
    assert ticket_dict['price'] == ticket.price
    assert ticket_dict['quantity'] == 1
    assert ticket_dict['ticket_fee'] == 0.0
    assert ticket_dict['sub_total'] == 0.0
    assert ticket_dict['discount']['total'] == 50.0
    assert ticket_dict['discount']['amount'] == 50.0
    assert ticket_dict['discount']['percent'] == 100.0
    assert ticket_dict['discount']['code'] == discount_code.code


def _assert_tax_data_discount(amount_data):
    assert amount_data['tax']['percent'] == 18.0
    assert amount_data['tax']['name'] == 'GST'
    assert amount_data['discount'] == 419.43
    assert amount_data['tickets'][0]['discount'] is None
    assert amount_data['tickets'][0]['sub_total'] == 247.0
    assert amount_data['tickets'][1]['discount'] == {
        'code': 'example',
        'percent': 10.0,
        'amount': 45.63,
        'total': 182.52,
        'type': 'percent',
    }
    assert amount_data['tickets'][1]['sub_total'] == 1642.68
    assert amount_data['tickets'][2]['discount'] == {
        'code': 'example',
        'percent': 10.0,
        'amount': 78.97,
        'total': 236.91,
        'type': 'percent',
    }
    assert amount_data['tickets'][2]['sub_total'] == 2132.19
    assert amount_data['tickets'][3]['discount'] is None
    assert amount_data['tickets'][3]['sub_total'] == 0.0


def test_tax_included_with_discount(db):
    discount_code = DiscountCodeTicketSubFactory(type='percent', value=10.0, tickets=[])
    tickets_dict = _create_taxed_tickets(db, discount_code=discount_code)

    amount_data = calculate_order_amount(tickets_dict, discount_code=discount_code)

    assert amount_data['sub_total'] == 4021.87
    assert amount_data['total'] == 4021.87
    assert amount_data['tax']['included'] is True
    _assert_tax_data_discount(amount_data)
    assert amount_data['tax']['amount'] == 613.51


def test_tax_excluded_with_discount(db):
    discount_code = DiscountCodeTicketSubFactory(type='percent', value=10.0, tickets=[])
    tickets_dict = _create_taxed_tickets(
        db, tax_included=False, discount_code=discount_code
    )

    amount_data = calculate_order_amount(tickets_dict, discount_code=discount_code)

    assert amount_data['sub_total'] == 4021.87
    assert amount_data['total'] == 4745.81
    assert amount_data['tax']['included'] is False
    _assert_tax_data_discount(amount_data)
    assert amount_data['tax']['amount'] == 723.94


def test_deleted_ticket(db):
    ticket = TicketSubFactory(deleted_at=datetime.now())
    db.session.commit()

    with pytest.raises(ObjectNotFound):
        calculate_order_amount([{'id': ticket.id}])


def test_ticket_of_deleted_event(db):
    ticket = TicketSubFactory(event__deleted_at=datetime.now())
    db.session.commit()

    with pytest.raises(ObjectNotFound):
        calculate_order_amount([{'id': ticket.id}])


def test_ticket_with_deleted_discount_code(db):
    ticket = TicketSubFactory()
    discount = DiscountCodeTicketSubFactory(deleted_at=datetime.now(), tickets=[ticket])

    db.session.commit()

    with pytest.raises(ObjectNotFound):
        calculate_order_amount([{'id': ticket.id}], discount_code=discount.id)


def test_ticket_with_different_discount_code(db):
    ticket = TicketSubFactory()
    discount = DiscountCodeTicketSubFactory(tickets=[])
    db.session.commit()

    with pytest.raises(UnprocessableEntityError, match='Invalid Discount Code'):
        calculate_order_amount([{'id': ticket.id}], discount_code=discount.id)


def test_request_calculate_order_amount(client, db):
    discount_code = DiscountCodeTicketSubFactory(type='percent', value=10.0, tickets=[])
    tickets_dict = _create_taxed_tickets(
        db, tax_included=False, discount_code=discount_code
    )
    db.session.commit()

    response = client.post(
        '/v1/orders/calculate-amount',
        content_type='application/json',
        data=json.dumps(
            {
                'tickets': tickets_dict,
                'discount-code': str(discount_code.id),
                'discount_verify': True,
            }
        ),
    )

    assert response.status_code == 200
    amount_data = json.loads(response.data)
    assert amount_data['sub_total'] == 4021.87
    assert amount_data['total'] == 4745.81
    assert amount_data['tax']['included'] is False
    _assert_tax_data_discount(amount_data)
    assert amount_data['tax']['amount'] == 723.94


def test_request_calculate_order_amount_without_discount(client, db):
    tickets_dict = _create_taxed_tickets(db, tax_included=False)

    response = client.post(
        '/v1/orders/calculate-amount',
        content_type='application/json',
        data=json.dumps({'tickets': tickets_dict}),
    )

    assert response.status_code == 200
    amount_data = json.loads(response.data)
    assert amount_data['sub_total'] == 4441.3
    assert amount_data['total'] == pytest.approx(4441.3 + 799.43)
    assert amount_data['tax']['included'] is False
    assert amount_data['tax']['percent'] == 18.0
    assert amount_data['tax']['amount'] == 799.43
    assert amount_data['discount'] == 0.0


def test_request_error(client, db):
    ticket = TicketSubFactory()
    discount = DiscountCodeTicketSubFactory(tickets=[])
    db.session.commit()

    response = client.post(
        '/v1/orders/calculate-amount',
        content_type='application/json',
        data=json.dumps({'tickets': [{'id': ticket.id}], 'discount-code': discount.id}),
    )

    assert response.status_code == 422
    assert json.loads(response.data) == {
        "errors": [
            {
                "status": 422,
                "source": {"pointer": "discount_code_id"},
                "title": "Unprocessable Entity",
                "detail": "Invalid Discount Code",
            }
        ],
        "jsonapi": {"version": "1.0"},
    }
