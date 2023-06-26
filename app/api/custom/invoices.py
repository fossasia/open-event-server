import os

from flask import Blueprint
from flask.helpers import send_from_directory
from flask_jwt_extended import current_user, jwt_required
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.orm.exc import NoResultFound

from app.api.auth import return_file
from app.api.custom.orders import order_blueprint
from app.api.helpers.errors import ForbiddenError, NotFoundError
from app.api.helpers.order import create_pdf_tickets_for_holder
from app.api.helpers.permission_manager import has_access
from app.api.helpers.storage import UPLOAD_PATHS, generate_hash
from app.models.event_invoice import EventInvoice
from app.models.order import Order

event_blueprint = Blueprint('event_blueprint', __name__, url_prefix='/v1/events')


@event_blueprint.route('/invoices/<string:invoice_identifier>')
@jwt_required
def event_invoices(invoice_identifier):
    if not current_user:
        raise ForbiddenError({'source': ''}, 'Authentication Required to access Invoice')
    try:
        event_invoice = EventInvoice.query.filter_by(
            identifier=invoice_identifier
        ).first()
        event_id = event_invoice.event_id
    except NoResultFound:
        raise NotFoundError({'source': ''}, 'Event Invoice not found')
    if not current_user.is_organizer(event_id) and not current_user.is_staff:
        raise ForbiddenError({'source': ''}, 'Unauthorized Access')
    key = UPLOAD_PATHS['pdf']['event_invoices'].format(identifier=invoice_identifier)
    file_path = (
        f'../generated/invoices/{key}/{generate_hash(key)}/{invoice_identifier}.pdf'
    )
    try:
        return return_file('event-invoice', file_path, invoice_identifier)
    except FileNotFoundError:
        raise ObjectNotFound(
            {'source': ''},
            "The Event Invoice isn't available at the moment. \
                             Invoices are usually issued on the 1st of every month",
        )


@order_blueprint.route('/invoices/<string:order_identifier>')
@jwt_required
def order_invoices(order_identifier):
    if current_user:
        try:
            order = Order.query.filter_by(identifier=order_identifier).first()
        except NoResultFound:
            raise NotFoundError({'source': ''}, 'Order Invoice not found')
        if has_access(
            'is_coorganizer_or_user_itself',
            event_id=order.event_id,
            user_id=order.user_id,
        ) or order.is_attendee(current_user):
            file_path = order.invoice_pdf_path
            if not os.path.isfile(file_path):
                create_pdf_tickets_for_holder(order)
            return send_from_directory('../', file_path, as_attachment=True)
        else:
            raise ForbiddenError({'source': ''}, 'Unauthorized Access')
    else:
        raise ForbiddenError({'source': ''}, 'Authentication Required to access Invoice')
