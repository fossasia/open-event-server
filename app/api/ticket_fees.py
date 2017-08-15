from flask_rest_jsonapi import ResourceDetail, ResourceList

from app import db
from app.api.bootstrap import api
from app.api.schema.ticket_fees import TicketFeesSchema
from app.models.ticket_fee import TicketFees


class TicketFeeList(ResourceList):
    """
    List and create TicketFees
    """
    decorators = (api.has_permission('is_admin'),)
    schema = TicketFeesSchema
    data_layer = {'session': db.session,
                  'model': TicketFees}


class TicketFeeDetail(ResourceDetail):
    """
    ticket_fee detail by id
    """
    decorators = (api.has_permission('is_admin'),)
    schema = TicketFeesSchema
    data_layer = {'session': db.session,
                  'model': TicketFees}
