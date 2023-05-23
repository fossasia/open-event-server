import logging
from datetime import datetime

import pytz
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.db import get_count, safe_query_by_id, save_to_db
from app.api.helpers.errors import ConflictError, UnprocessableEntityError
from app.api.helpers.order import delete_related_attendees_for_order, on_order_completed
from app.api.helpers.payment import PayPalPaymentsManager, StripePaymentsManager
from app.models import db
from app.models.ticket import Ticket
from app.models.ticket_fee import TicketFees
from app.models.ticket_holder import TicketHolder

logger = logging.getLogger(__name__)


def validate_ticket_holders(ticket_holder_ids):
    # pytype: disable=attribute-error
    ticket_holders = (
        TicketHolder.query.filter_by(deleted_at=None)
        .filter(TicketHolder.id.in_(ticket_holder_ids))
        .all()
    )
    # pytype: enable=attribute-error

    if len(ticket_holders) != len(ticket_holder_ids):
        logger.warning(
            "Ticket Holders not found in", extra=dict(ticket_holder_ids=ticket_holder_ids)
        )
        raise ObjectNotFound(
            {'pointer': '/data/relationships/attendees'},
            "Some attendee among ids {str(ticket_holder_ids)} do not exist",
        )

    for ticket_holder in ticket_holders:
        # Ensuring that the attendee exists and doesn't have an associated order.
        if ticket_holder.order_id:
            logger.warning(
                "Order already exists for attendee",
                extra=dict(attendee_id=ticket_holder.id),
            )
            raise ConflictError(
                {'pointer': '/data/relationships/attendees'},
                "Order already exists for attendee with id {}".format(
                    str(ticket_holder.id)
                ),
            )
    return ticket_holders


def validate_tickets(tickets):
    """Validates that all tickets are not deleted and belong to same event"""
    if not tickets:
        return tickets
    fetched_tickets = (
        Ticket.query.filter_by(deleted_at=None).filter(Ticket.id.in_(tickets)).all()
    )
    # All passed tickets should not be deleted and their event should be same
    if len(fetched_tickets) != len(tickets):
        logger.warning("Deleted tickets requested for Order", extra=dict(tickets=tickets))
        raise ObjectNotFound(
            {'pointer': 'tickets'}, f'Tickets not found for IDs: {tickets}'
        )
    ticket_events = {ticket.event_id for ticket in fetched_tickets}
    if len(ticket_events) != 1:
        logger.warning(
            "Tickets with different event IDs requested for Order",
            extra=dict(ticket_events=ticket_events),
        )
        raise UnprocessableEntityError(
            {'pointer': 'tickets'},
            f'All tickets must belong to same event. Found: {ticket_events}',
        )
    return fetched_tickets


def validate_discount_code(
    discount_code, tickets=None, ticket_holders=None, event_id=None
):
    """Tickets validation should be performed before calling this function"""
    from app.models.discount_code import DiscountCode

    if isinstance(discount_code, int) or (
        isinstance(discount_code, str) and discount_code.isdigit()
    ):
        # Discount Code ID is passed
        discount_code = safe_query_by_id(DiscountCode, discount_code)

    if not tickets and not ticket_holders:
        raise ValueError('Need to provide either tickets or ticket_holders')

    # Otherwise actual instance of Discount Code is passed

    if event_id:
        if discount_code.event.id != int(event_id):
            logger.warning(
                "Discount code Event ID mismatch",
                extra=dict(event_id=event_id, discount_code=discount_code),
            )
            raise UnprocessableEntityError(
                {'pointer': 'discount_code_id'}, "Invalid Discount Code"
            )

    if tickets:
        ticket_applicable = discount_code.get_supported_tickets(
            [ticket['id'] for ticket in tickets]
        ).all()
        if len(ticket_applicable) < 1:
            logger.warning(
                "Discount code is not applicable to these tickets",
                extra=dict(
                    tickets=tickets,
                    applicable_tickets=ticket_applicable,
                    discount_code=discount_code,
                ),
            )
            raise UnprocessableEntityError(
                {'pointer': 'discount_code_id'}, 'Invalid Discount Code'
            )

    now = pytz.utc.localize(datetime.utcnow())
    valid_from = discount_code.valid_from
    valid_till = discount_code.valid_expire_time
    if not discount_code.is_active or not valid_from <= now <= valid_till:
        logger.warning(
            "Discount code inactive or expired",
            extra=dict(
                discount_code=discount_code,
                active=discount_code.is_active,
                valid_from=valid_from,
                valid_till=valid_till,
                now=now,
            ),
        )
        raise UnprocessableEntityError(
            {'pointer': 'discount_code_id'}, "Invalid Discount Code"
        )
    # TODO: Need to check it correctly
    # if not discount_code.is_available(tickets, ticket_holders):
    #     raise UnprocessableEntityError(
    #         {'source': 'discount_code_id'}, 'Discount Usage Exceeded'
    #     )

    return discount_code


def is_discount_available(discount_code, tickets=None, ticket_holders=None):
    """
    Validation of discount code belonging to the tickets and events should be done
    before calling this method
    """
    qty = 0
    # TODO(Areeb): Extremely confusing here what should we do about deleted tickets here
    ticket_ids = [ticket.id for ticket in discount_code.tickets]
    old_holders = discount_code.confirmed_attendees_count
    if ticket_holders:
        # pytype: disable=attribute-error
        qty = get_count(
            TicketHolder.query.filter(
                TicketHolder.id.in_(ticket_holders),
                TicketHolder.ticket_id.in_(ticket_ids),
            )
        )
        # pytype: enable=attribute-error
    elif tickets:
        for ticket in tickets:
            if int(ticket['id']) in ticket_ids:
                qty += ticket.get('quantity', 1)

    max_quantity = qty if discount_code.max_quantity < 0 else discount_code.max_quantity

    available = (
        (qty + old_holders) <= discount_code.tickets_number
        and discount_code.min_quantity <= qty <= max_quantity
    )
    if not available:
        logger.warning(
            "Discount code usage exhausted",
            extra=dict(
                discount_code=discount_code,
                ticket_ids=ticket_ids,
                ticket_holders=ticket_holders,
                quantity=qty,
                old_holders=old_holders,
            ),
        )
    return available


class TicketingManager:
    """All ticketing and orders related helper functions"""

    # TODO(Areeb): Remove after validating logic
    @staticmethod
    def calculate_update_amount(order):
        discount = None
        if order.discount_code_id:
            discount = order.discount_code
        # Access code part will be done ticket_holders API
        amount = 0
        total_discount = 0
        fees = TicketFees.query.filter_by(currency=order.event.payment_currency).first()

        for order_ticket in order.order_tickets:
            with db.session.no_autoflush:
                if order_ticket.ticket.is_fee_absorbed or not fees:
                    ticket_amount = order_ticket.ticket.price * order_ticket.quantity
                    amount += order_ticket.ticket.price * order_ticket.quantity
                else:
                    order_fee = (
                        fees.service_fee
                        * (order_ticket.ticket.price * order_ticket.quantity)
                        / 100
                    )
                    if order_fee > fees.maximum_fee:
                        ticket_amount = (
                            order_ticket.ticket.price * order_ticket.quantity
                        ) + fees.maximum_fee
                        amount += (
                            order_ticket.ticket.price * order_ticket.quantity
                        ) + fees.maximum_fee
                    else:
                        ticket_amount = (
                            order_ticket.ticket.price * order_ticket.quantity
                        ) + order_fee
                        amount += (
                            order_ticket.ticket.price * order_ticket.quantity
                        ) + order_fee

                if discount and str(order_ticket.ticket.id) in discount.tickets.split(
                    ","
                ):
                    if discount.type == "amount":
                        total_discount += discount.value * order_ticket.quantity
                    else:
                        total_discount += discount.value * ticket_amount / 100

        if discount:
            if discount.type == "amount":
                order.amount = max(amount - total_discount, 0)
            elif discount.type == "percent":
                order.amount = amount - (discount.value * amount / 100.0)
        else:
            order.amount = amount
        save_to_db(order)
        return order

    @staticmethod
    def create_payment_intent_for_order_stripe(order):
        """
        Create payment intent for order
        :param order: Order for which to charge for
        :return:
        """
        # create payment intent for the user
        try:
            payment_intent = StripePaymentsManager.get_payment_intent_stripe(order)
            order.stripe_payment_intent_id = payment_intent['id']
            db.session.commit()
            return True, payment_intent
        except ConflictError as e:
            # payment intent creation failed hence expire the order
            order.status = 'expired'
            save_to_db(order)

            # delete related attendees to unlock the tickets
            delete_related_attendees_for_order(order)

            # return the failure message from stripe.
            return False, e

    @staticmethod
    def charge_paypal_order_payment(order, paypal_payer_id, paypal_payment_id):
        """
        Charge the user through paypal.
        :param order: Order for which to charge for.
        :param paypal_payment_id: payment_id
        :param paypal_payer_id: payer_id
        :return:
        """

        # save the paypal payment_id with the order
        order.paypal_token = paypal_payment_id
        save_to_db(order)

        # create the transaction.
        status, error = PayPalPaymentsManager.execute_payment(
            paypal_payer_id, paypal_payment_id
        )

        if status:
            # successful transaction hence update the order details.
            order.paid_via = 'paypal'
            order.status = 'completed'
            order.transaction_id = paypal_payment_id
            order.completed_at = datetime.utcnow()
            save_to_db(order)

            on_order_completed(order)

            return True, 'Charge successful'
        # payment failed hence expire the order
        order.status = 'expired'
        save_to_db(order)

        # delete related attendees to unlock the tickets
        delete_related_attendees_for_order(order)

        # return the error message from Paypal
        return False, error
