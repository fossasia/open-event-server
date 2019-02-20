from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema
from flask_rest_jsonapi import ResourceList

from app.api.helpers.utilities import dasherize
from app.api.bootstrap import api
from app.models import db
from app.models.event import Event
from app.models.order import Order, OrderTicket
from app.models.role import Role
from app.models.user import User
from app.models.users_events_role import UsersEventsRoles

from app.api.admin_sales.utils import summary


class AdminSalesByOrganizersSchema(Schema):
    """
    Sales summarized by organizer

    Provides
        organizer (first name, last name and email),
        count of tickets and total sales for orders grouped by status
    """

    class Meta:
        type_ = 'admin-sales-by-organizers'
        self_view = 'v1.admin_sales_by_organizers'
        inflect = dasherize

    id = fields.String()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.String()
    starts_at = fields.DateTime()
    ends_at = fields.DateTime()
    sales = fields.Method('calc_sales')

    @staticmethod
    def calc_sales(obj):
        """
        Returns sales (dictionary with total sales and ticket count) for
        placed, completed and pending orders
        """
        return summary(obj.orders)


class AdminSalesByOrganizersList(ResourceList):
    """
    Resource for sales by organizers. Joins organizers with events and orders
    and subsequently accumulates sales by status
    """

    def query(self, _):
        query_ = self.session.query(User)
        query_ = query_.join(UsersEventsRoles).filter(Role.name == 'organizer')
        query_ = query_.join(Event).outerjoin(Order).outerjoin(OrderTicket)

        return query_

    methods = ['GET']
    decorators = (api.has_permission('is_admin'), )
    schema = AdminSalesByOrganizersSchema
    data_layer = {
        'model': User,
        'session': db.session,
        'methods': {
            'query': query
        }
    }
