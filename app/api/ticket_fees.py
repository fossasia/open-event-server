from flask_rest_jsonapi import ResourceDetail, ResourceList
from sqlalchemy.orm.exc import NoResultFound

from app import db
from app.api.bootstrap import api
from app.api.helpers.exceptions import ConflictException, UnprocessableEntity
from app.api.schema.ticket_fees import TicketFeesSchema
from app.models.ticket_fee import TicketFees


class TicketFeeList(ResourceList):
    """
    List and create TicketFees
    """
    def before_post(self, args, kwargs, data):
        """
        before post method to check for existing currency-country combination
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        if 'country' in data and 'currency' in data:
            if data['country'] and data['currency']:
                try:
                    TicketFees.query.filter_by(country=data['country'], currency=data['currency']).one()
                except NoResultFound:
                    pass
                else:
                    raise ConflictException(
                        {'pointer': ''},
                        "({}-{}) Combination already exists".format(data['currency'], data['country']))
            else:
                raise UnprocessableEntity({'source': ''}, "Country or Currency cannot be NULL")
        else:
            raise UnprocessableEntity({'source': ''}, "Country or Currency Attribute is missing")

    decorators = (api.has_permission('is_admin'),)
    schema = TicketFeesSchema
    data_layer = {'session': db.session,
                  'model': TicketFees,
                  'methods': {'before_post': before_post}
                  }


class TicketFeeDetail(ResourceDetail):
    """
    ticket_fee detail by id
    """
    decorators = (api.has_permission('is_admin'),)
    schema = TicketFeesSchema
    data_layer = {'session': db.session,
                  'model': TicketFees}
