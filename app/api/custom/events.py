from flask import Blueprint
from flask_rest_jsonapi.exceptions import ObjectNotFound
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.orm.exc import NoResultFound


from app.api.auth import return_file
from app.api.helpers.errors import ForbiddenError, NotFoundError
from app.api.helpers.storage import generate_hash, UPLOAD_PATHS
from app.models.event_invoice import EventInvoice

event_blueprint = Blueprint('event_blueprint', __name__, url_prefix='/v1/events')


@event_blueprint.route('/invoices/<string:invoice_identifier>')
@jwt_required
def event_invoices(invoice_identifier):
    if not current_user:
        return ForbiddenError({'source': ''}, 'Authentication Required to access Invoice').respond()
    try:
        event_invoice = EventInvoice.query.filter_by(identifier=invoice_identifier).first()
        event_id = event_invoice.event_id
    except NoResultFound:
        return NotFoundError({'source': ''}, 'Event Invoice not found').respond()
    if not current_user.is_organizer(event_id) and not current_user.is_staff:
        return ForbiddenError({'source': ''}, 'Unauthorized Access').respond()
    key = UPLOAD_PATHS['pdf']['event_invoices'].format(identifier=invoice_identifier)
    file_path = '../generated/invoices/{}/{}/'.format(key, generate_hash(key)) + invoice_identifier + '.pdf'
    try:
        return return_file('event-invoice', file_path, invoice_identifier)
    except FileNotFoundError:
        raise ObjectNotFound({'source': ''},
                             "The Event Invoice isn't available at the moment. \
                             Invoices are usually issued on the 1st of every month")
