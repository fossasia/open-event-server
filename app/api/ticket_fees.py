from flask_rest_jsonapi import ResourceDetail, ResourceList
from sqlalchemy.orm.exc import NoResultFound
from app import db
from app.api.bootstrap import api
from app.api.schema.ticket_fees import TicketFeesSchema
from app.models.ticket_fee import TicketFees
from app.api.helpers.exceptions import ConflictException


class TicketFeeList(ResourceList):
    """
    List and create TicketFees
    """

    def before_post(self, args, kwargs, data):
        """
        method to check for existing country currency combination
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        if (data['country'] and data['currency']):
            try:
                already_existing_combination = TicketFees.query.filter_by(country=data['country'],
                                                                          currency=data['currency']).one()
                if already_existing_combination:
                    raise ConflictException({'pointer': 'data/attributes/country'}, 'Combination Exists')
            except NoResultFound:
                pass

    decorators = (api.has_permission('is_admin'),)
    schema = TicketFeesSchema
    data_layer = {'session': db.session,
                  'model': TicketFees}


class TicketFeeDetail(ResourceDetail):
    """
    ticket_fee detail by id
    """

    def before_patch(self, args, kwargs, data):
        """
        method to check if patched combination id is same as new one
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        if (data['country'] and data['currency']):
            try:
                already_existing_combination = TicketFees.query.filter_by(country=data['country'],
                                                                          currency=data['currency']).one()
                if already_existing_combination.id != kwargs['id']:
                    raise ConflictException({'pointer': 'data/attributes/country'}, 'Combination Exists')
            except NoResultFound:
                pass

    decorators = (api.has_permission('is_admin'),)
    schema = TicketFeesSchema
    data_layer = {'session': db.session,
                  'model': TicketFees}
