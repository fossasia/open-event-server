from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema
from flask_rest_jsonapi import ResourceList

from app.api.bootstrap import api
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.event_invoice import EventInvoice


class AdminSalesInvoicesSchema(Schema):
    """
    Sales invoices
    """

    class Meta:
        type_ = 'admin-sales-invoices'
        self_view = 'v1.admin_sales_invoices'
        inflect = dasherize

    id = fields.String()
    identifier = fields.String()
    status = fields.String()
    amount = fields.Float()
    created_at = fields.DateTime()
    completed_at = fields.DateTime()
    event_name = fields.Method('format_event_name')
    sent_to = fields.Method('format_sent_to')

    @staticmethod
    def format_event_name(self):
        return '{}'.format(self.event.name)

    @staticmethod
    def format_sent_to(self):
        return '{} <{}>'.format(self.user.fullname, self.user.email)


class AdminSalesInvoicesList(ResourceList):
    """
    Resource for sales invoices
    """

    methods = ['GET']
    decorators = (api.has_permission('is_admin'), )
    schema = AdminSalesInvoicesSchema
    data_layer = {'model': EventInvoice, 'session': db.session}
