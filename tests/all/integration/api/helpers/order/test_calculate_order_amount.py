from app.api.helpers.order import calculate_order_amount
from tests.factories.tax import TaxSubFactory
from tests.factories.ticket import TicketFactory, TicketSubFactory, TicketFactoryBase


def test_no_amount():
    amount_data = calculate_order_amount([])

    assert amount_data['total_amount'] == 0.0
    assert amount_data['tax_included'] is None
    assert amount_data['total_tax'] == 0.0
    assert amount_data['total_discount'] == 0.0
    assert amount_data['tickets'] == []


def test_single_ticket(db):
    ticket = TicketSubFactory(price=10)
    db.session.commit()

    amount_data = calculate_order_amount([{'id': ticket.id}])

    assert amount_data['total_amount'] == 10.0
    assert amount_data['tax_included'] is None
    assert amount_data['total_tax'] == 0.0
    assert amount_data['total_discount'] == 0.0
    ticket_dict = amount_data['tickets'][0]
    assert ticket_dict['id'] == ticket.id
    assert ticket_dict['name'] == ticket.name
    assert ticket_dict['price'] == ticket.price
    assert ticket_dict['quantity'] == 1
    assert ticket_dict['ticket_fee'] == 0.0
    assert ticket_dict['sub_total'] == 10.0


def _create_ticket_dict(tickets, quantities):
    return [dict(id=ticket.id, quantity=quantity) for ticket, quantity in zip(tickets, quantities)]


def test_multiple_tickets(db):
    ticket = TicketSubFactory(price=50)
    ticket2 = TicketSubFactory(price=12.5, event=ticket.event)
    ticket3 = TicketSubFactory(price=233.15, event=ticket.event)
    db.session.commit()

    tickets = _create_ticket_dict([ticket, ticket2, ticket3], [3, 1, 2])

    amount_data = calculate_order_amount(tickets)

    assert amount_data['total_amount'] == 628.8
    assert amount_data['tax_included'] is None
    assert amount_data['total_tax'] == 0.0
    assert amount_data['total_discount'] == 0.0
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


def test_tax_included(db):
    tax = TaxSubFactory(rate=18.0, is_tax_included_in_price=True)
    tickets = _create_tickets([123.5, 456.3, 789.7], event=tax.event)
    db.session.commit()

    tickets_dict = _create_ticket_dict(tickets, [2, 4, 3])

    amount_data = calculate_order_amount(tickets_dict)

    assert amount_data['total_amount'] == 4441.3
    assert amount_data['tax_included'] is True
    assert amount_data['total_tax'] == 799.43
    assert amount_data['total_discount'] == 0.0
