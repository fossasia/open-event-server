from flask import Blueprint
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.orm.exc import NoResultFound


from app.api.auth import return_file
from app.api.helpers.errors import ForbiddenError, NotFoundError
from app.api.helpers.order import create_pdf_tickets_for_holder
from app.api.helpers.storage import UPLOAD_PATHS
from app.api.helpers.storage import generate_hash
from app.models.order import Order

ticket_blueprint = Blueprint('ticket_blueprint', __name__, url_prefix='/v1/tickets')


@ticket_blueprint.route('/<string:order_identifier>')
@jwt_required
def ticket_attendee_authorized(order_identifier):
    if current_user:
        try:
            order = Order.query.filter_by(identifier=order_identifier).first()
        except NoResultFound:
            return NotFoundError({'source': ''}, 'This ticket is not associated with any order').respond()
        if current_user.can_download_tickets(order):
            key = UPLOAD_PATHS['pdf']['tickets_all'].format(identifier=order_identifier)
            file_path = '../generated/tickets/{}/{}/'.format(key, generate_hash(key)) + order_identifier + '.pdf'
            try:
                return return_file('ticket', file_path, order_identifier)
            except FileNotFoundError:
                create_pdf_tickets_for_holder(order)
                return return_file('ticket', file_path, order_identifier)
        else:
            return ForbiddenError({'source': ''}, 'Unauthorized Access').respond()
    else:
        return ForbiddenError({'source': ''}, 'Authentication Required to access ticket').respond()
