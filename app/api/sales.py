from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema
from flask_rest_jsonapi import ResourceList

from app.api.bootstrap import api
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.event import Event


class SalesSchema(Schema):
    """
    Gross Sales (The grand total of all sale transactions reported in a period,
    without any deductions included within the figure ) minus the following three
    deductions:

    - Sales allowances. A reduction in the price paid by a customer, due to minor
    product defects. The seller grants a sales allowance after the buyer has
    purchased the items in question.

    - Sales discounts. An early payment discount, such as paying 2% less if the
    buyer pays within 10 days of the invoice date. The seller does not know
    which customers will take the discount at the time of sale, so the discount
    is typically applied upon the receipt of cash from customers.

    - Sales returns. A refund granted to customers if they return goods to the
    company (typically under a return merchandise authorization).
    """

    class Meta:
        type_ = 'sales'
        self_view = 'v1.sales'
        inflect = dasherize

    id = fields.String()


class AdminSalesInvoicesList(ResourceList):
    """
    TODO create
    """

    methods = ['GET']
    decorators = (jwt_required,)
    schema = SalesSchema
    data_layer = {'model': Event, 'session': db.session}
