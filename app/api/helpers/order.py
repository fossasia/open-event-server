import logging
from datetime import datetime, timedelta, timezone

from flask import render_template
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.db import (
    get_count,
    safe_query_without_soft_deleted_entries,
    save_to_db,
)
from app.api.helpers.errors import ConflictError, UnprocessableEntityError
from app.api.helpers.files import create_save_pdf
from app.api.helpers.mail import (
    convert_to_user_locale,
    send_email_to_attendees,
    send_order_purchase_organizer_email,
)
from app.api.helpers.notification import (
    notify_ticket_purchase_attendee,
    notify_ticket_purchase_organizer,
)
from app.api.helpers.storage import UPLOAD_PATHS
from app.models import db
from app.models.order import OrderTicket
from app.models.setting import Setting
from app.models.ticket import Ticket
from app.models.ticket_fee import TicketFees
from app.models.ticket_holder import TicketHolder
from app.settings import get_settings


def delete_related_attendees_for_order(order):
    """
    Delete the associated attendees of an order when it is cancelled/deleted/expired
    :param order: Order whose attendees have to be deleted.
    :return:
    """
    for ticket_holder in order.ticket_holders:
        db.session.delete(ticket_holder)
        try:
            db.session.commit()
        except Exception:
            logging.exception('DB Exception!')
            db.session.rollback()


def set_expiry_for_order(order, override=False):
    """
    Expire the order after the time slot(10 minutes) if the order is initializing.
    Also expires the order if we want to expire an order regardless of the state and time.
    :param order: Order to be expired.
    :param override: flag to force expiry.
    :return:
    """
    order_expiry_time = get_settings()['order_expiry_time']
    if (
        order
        and not order.paid_via
        and (
            override
            or (
                order.status == 'initializing'
                and (order.created_at + timedelta(minutes=order_expiry_time))
                < datetime.now(timezone.utc)
            )
        )
    ):
        order.status = 'expired'
        delete_related_attendees_for_order(order)
        save_to_db(order)
    return order


def create_pdf_tickets_for_holder(order):
    """
    Create tickets and invoices for the holders of an order.
    :param order: The order for which to create tickets for.
    """
    starts_at = convert_to_user_locale(
        order.user.email, date_time=order.event.starts_at, tz=order.event.timezone
    )
    ends_at = convert_to_user_locale(
        order.user.email, date_time=order.event.ends_at, tz=order.event.timezone
    )
    admin_info = Setting.query.first()
    if order.status == 'completed' or order.status == 'placed':
        pdf = create_save_pdf(
            render_template(
                'pdf/ticket_purchaser.html',
                order=order,
                app_name=get_settings()['app_name'],
                admin_info=admin_info,
                starts_at=starts_at,
                ends_at=ends_at,
            ),
            UPLOAD_PATHS['pdf']['tickets_all'],
            dir_path='/static/uploads/pdf/tickets/',
            identifier=order.identifier,
            extra_identifiers={'extra_identifier': order.identifier},
            upload_dir='generated/tickets/',
        )

        order.tickets_pdf_url = pdf

        for holder in order.ticket_holders:
            starts_at = convert_to_user_locale(
                holder.email, date_time=order.event.starts_at, tz=order.event.timezone
            )
            ends_at = convert_to_user_locale(
                holder.email, date_time=order.event.ends_at, tz=order.event.timezone
            )

            # create attendee pdf for every ticket holder
            pdf = create_save_pdf(
                render_template(
                    'pdf/ticket_attendee.html',
                    order=order,
                    holder=holder,
                    app_name=get_settings()['app_name'],
                    admin_info=admin_info,
                    starts_at=starts_at,
                    ends_at=ends_at,
                ),
                UPLOAD_PATHS['pdf']['tickets_all'],
                dir_path='/static/uploads/pdf/tickets/',
                identifier=order.identifier,
                extra_identifiers={'extra_identifier': holder.id},
                upload_dir='generated/tickets/',
            )
            holder.pdf_url = pdf
            save_to_db(holder)

        # create order invoices pdf
        order_tickets = OrderTicket.query.filter_by(order_id=order.id).all()

        tickets = []
        for order_ticket in order_tickets:
            attendee_count = get_count(
                TicketHolder.query.filter_by(order_id=order_ticket.order.id)
                .filter_by(ticket_id=order_ticket.ticket.id)
                .filter_by(is_discount_applied=True)
            )
            ticket = dict(
                id=order_ticket.ticket.id,
                price=order_ticket.price,
                quantity=order_ticket.quantity,
                quantity_discount=attendee_count,
            )
            tickets.append(ticket)

        # calculate order amount using helper function
        order_amount = calculate_order_amount(
            tickets, verify_discount=False, discount_code=order.discount_code
        )

        create_save_pdf(
            render_template(
                'pdf/order_invoice.html',
                order=order,
                event=order.event,
                tax=order.event.tax,
                order_tickets=order_tickets,
                event_starts_at=convert_to_user_locale(
                    order.user.email,
                    date=order.event.starts_at_tz,
                ),
                created_at=convert_to_user_locale(
                    order.user.email,
                    date=order.created_at,
                ),
                admin_info=admin_info,
                order_amount=order_amount,
            ),
            UPLOAD_PATHS['pdf']['order'],
            dir_path='/static/uploads/pdf/tickets/',
            identifier=order.identifier,
            upload_dir='generated/invoices/',
            new_renderer=True,
        )
        save_to_db(order)


def create_onsite_attendees_for_order(data):
    """
    Creates on site ticket holders for an order and adds it into the request data.
    :param data: data initially passed in the POST request for order.
    :return:
    """
    on_site_tickets = data.get('on_site_tickets')

    if not on_site_tickets:
        raise UnprocessableEntityError(
            {'pointer': 'data/attributes/on_site_tickets'}, 'on_site_tickets info missing'
        )

    data['ticket_holders'] = []

    for on_site_ticket in on_site_tickets:
        ticket_id = on_site_ticket['id']
        quantity = int(on_site_ticket['quantity'])

        ticket = safe_query_without_soft_deleted_entries(
            Ticket, 'id', ticket_id, 'ticket_id'
        )

        ticket_sold_count = get_count(
            db.session.query(TicketHolder.id).filter_by(
                ticket_id=int(ticket.id), deleted_at=None
            )
        )

        # Check if the ticket is already sold out or not.
        if ticket_sold_count + quantity > ticket.quantity:
            # delete the already created attendees.
            for holder in data['ticket_holders']:
                ticket_holder = (
                    db.session.query(TicketHolder).filter(id == int(holder)).one()
                )
                db.session.delete(ticket_holder)
                try:
                    db.session.commit()
                except Exception:
                    logging.exception('DB Exception!')
                    db.session.rollback()

            raise ConflictError(
                {'pointer': '/data/attributes/on_site_tickets'},
                "Ticket with id: {} already sold out. You can buy at most {} tickets".format(
                    ticket_id, ticket.quantity - ticket_sold_count
                ),
            )

        for _ in range(1, quantity):
            ticket_holder = TicketHolder(
                firstname='onsite',
                lastname='attendee',
                email='example@example.com',
                ticket_id=ticket.id,
                event_id=data.get('event'),
            )
            save_to_db(ticket_holder)
            data['ticket_holders'].append(ticket_holder.id)

    # delete from the data.
    del data['on_site_tickets']


def calculate_order_amount(tickets, verify_discount=True, discount_code=None):
    from app.api.helpers.ticketing import (
        is_discount_available,
        validate_discount_code,
        validate_tickets,
    )
    from app.models.discount_code import DiscountCode

    ticket_ids = {ticket['id'] for ticket in tickets}
    ticket_map = {int(ticket['id']): ticket for ticket in tickets}
    fetched_tickets = validate_tickets(ticket_ids)
    quantity_discount: dict = {'numb_no_discount': 0, 'numb_discount': 0}

    if tickets and discount_code:
        discount_code = validate_discount_code(discount_code, tickets=tickets)
        quantity_discount = is_discount_available(
            discount_code,
            tickets=tickets,
            quantity_discount=quantity_discount,
            verify_discount=verify_discount,
        )

    event = tax = tax_included = fees = None
    total_amount = total_discount = 0.0
    ticket_list = []
    for ticket in fetched_tickets:
        ticket_tax = discounted_tax = 0.0
        ticket_info = ticket_map[ticket.id]
        discount_amount = 0.0
        discount_data = None
        ticket_fee = 0.0

        quantity = ticket_info.get('quantity', 1)  # Default to single ticket
        if ticket_info.get('quantity_discount'):
            quantity_discount['numb_discount'] = ticket_info.get('quantity_discount')
        discount_quantity = (
            quantity
            if quantity_discount['numb_discount'] >= quantity
            else quantity_discount['numb_discount']
        )
        if not event:
            event, fees = get_event_fee(ticket)
        if not tax and event.tax:
            tax = event.tax
            tax_included = tax.is_tax_included_in_price
        price = get_price(ticket, ticket_info)
        if tax:
            ticket_tax = (
                price - price / (1 + tax.rate / 100)
                if tax_included
                else price * tax.rate / 100
            )
        if discount_code and ticket.type not in ['free', 'freeRegistration']:
            code = (
                DiscountCode.query.with_parent(ticket)
                .filter_by(id=discount_code.id)
                .first()
            )
            if code:
                if discount_code.id == code.id:
                    (
                        discount_amount,
                        discount_percent,
                        discounted_tax,
                    ) = get_discount_amount(
                        code, price, tax_included, tax, ticket_tax, discounted_tax
                    )
                    discount_data = get_discount_data(
                        discount_code,
                        discount_percent,
                        discount_amount,
                        discount_quantity,
                        code,
                        quantity_discount,
                    )
                quantity_discount['numb_discount'] = (
                    quantity_discount['numb_discount'] - quantity
                )

        total_discount += round(discount_amount * discount_quantity, 2)
        if fees and not ticket.is_fee_absorbed:
            ticket_fee = fees.service_fee * (price * quantity) / 100
            ticket_fee = min(ticket_fee, fees.maximum_fee)
        sub_total = ticket_fee + (price - discount_amount) * discount_quantity
        sub_total += price * max(0, quantity - discount_quantity)
        total_amount = total_amount + sub_total
        ticket_list.append(
            {
                'id': ticket.id,
                'name': ticket.name,
                'price': price,
                'quantity': quantity,
                'discount': discount_data,
                'ticket_fee': round(ticket_fee, 2),
                'sub_total': round(sub_total, 2),
                'ticket_tax': round(ticket_tax, 2),
                'discounted_tax': round(discounted_tax, 2),
            }
        )

    sub_total = total_amount
    tax_dict = None
    if tax:
        tax_dict, total_amount = get_tax_amount(tax_included, total_amount, tax)

    return dict(
        tax=tax_dict,
        sub_total=round(sub_total, 2),
        total=round(total_amount, 2),
        discount=round(total_discount, 2),
        tickets=ticket_list,
    )


def on_order_completed(order):
    # send e-mail and notifications if the order status is completed
    if not (order.status == 'completed' or order.status == 'placed'):
        return

    create_pdf_tickets_for_holder(order)

    # send email and notifications.
    send_email_to_attendees(order)
    notify_ticket_purchase_attendee(order)

    if order.payment_mode in ['free', 'bank', 'cheque', 'onsite']:
        order.completed_at = datetime.utcnow()

    organizer_set = set(
        filter(
            bool, order.event.organizers + order.event.coorganizers + [order.event.owner]
        )
    )
    send_order_purchase_organizer_email(order, organizer_set)
    notify_ticket_purchase_organizer(order)


def get_price(ticket, ticket_info):
    if ticket.type in ['donation', 'donationRegistration']:
        price = ticket_info.get('price')
        if not price or price > ticket.max_price or price < ticket.min_price:
            raise UnprocessableEntityError(
                {'pointer': 'tickets/price'},
                f"Price for donation ticket should be present and within range "
                f"{ticket.min_price} to {ticket.max_price}",
            )
    else:
        price = ticket.price if ticket.type not in ['free', 'freeRegistration'] else 0.0
    return price


def get_discount_data(
    discount_code,
    discount_percent,
    discount_amount,
    discount_quantity,
    code,
    quantity_discount,
):
    """
    Get discount data for calculate price
    @param discount_code: discount code
    @param discount_percent: discount percent
    @param discount_amount: discount amount
    @param discount_quantity: discount quantity
    @param code: code
    @param quantity_discount: quantity discount
    @return: discount data
    """
    discount_data = {
        'code': discount_code.code,
        'percent': round(discount_percent, 2),
        'amount': round(discount_amount, 2),
        'total': round(discount_amount * discount_quantity, 2),
        'type': code.type,
    }
    if int(quantity_discount.get('numb_no_discount')) > 0:
        discount_data[
            'warning'
        ] = 'Your order not fully discount due to discount code usage is exhausted.'
    return discount_data


def get_tax_amount(tax_included, total_amount, tax):
    """
    Get tax amount for calculate price
    @param tax_included: tax included
    @param total_amount: total amount
    @param tax: tax model
    @return: tax and amount after tax
    """
    if tax_included:
        total_tax = total_amount - total_amount / (1 + tax.rate / 100)
    else:
        total_tax = total_amount * tax.rate / 100
        total_amount += total_tax
    tax_dict = dict(
        included=tax_included,
        amount=round(total_tax, 2),
        percent=tax.rate if tax else 0.0,
        name=tax.name,
    )
    return tax_dict, total_amount


def get_event_fee(ticket):
    event = ticket.event

    if event.deleted_at:
        raise ObjectNotFound({'pointer': 'tickets/event'}, f'Event: {event.id} not found')

    fees = TicketFees.query.filter_by(currency=event.payment_currency).first()
    return event, fees


def get_discount_amount(code, price, tax_included, tax, ticket_tax, discounted_tax):
    if code.type == 'amount':
        discount_amount = min(code.value, price)
        discount_percent = (discount_amount / price) * 100
        if tax:
            tax_rate = tax.rate / 100
            tax_factor = 1 + tax_rate
            discounted_price = price - discount_amount
            discounted_tax = (
                discounted_price * tax_rate / tax_factor
                if tax_included
                else discounted_price * tax_rate
            )
    else:
        discount_amount = (price * code.value) / 100
        if tax:
            discounted_tax = ticket_tax - (ticket_tax * code.value / 100)
        discount_percent = code.value
    return discount_amount, discount_percent, discounted_tax
