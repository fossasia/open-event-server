from flask_rest_jsonapi import ResourceDetail
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields
from datetime import datetime, timedelta
import pytz

from app.api.helpers.utilities import dasherize
from app.api.bootstrap import api
from app.models import db
from app.models.mail import Mail
from app.api.data_layers.NoModelLayer import NoModelLayer


class AdminStatisticsMailSchema(Schema):
    """
    Api schema
    """
    class Meta:
        """
        Meta class
        """
        type_ = 'admin-statistics-mail'
        self_view = 'v1.admin_statistics_mail_detail'
        inflect = dasherize

    id = fields.String()
    one_day = fields.Method("mail_last_1_day")
    three_days = fields.Method("mail_last_3_days")
    seven_days = fields.Method("mail_last_7_days")
    thirty_days = fields.Method("mail_last_30_days")
    total = fields.Method("mail_total")

    def mail_last_1_day(self, obj):
        return Mail.query.filter(datetime.now(pytz.utc) - Mail.time <= timedelta(days=1)).count()

    def mail_last_3_days(self, obj):
        return Mail.query.filter(datetime.now(pytz.utc) - Mail.time <= timedelta(days=3)).count()

    def mail_last_7_days(self, obj):
        return Mail.query.filter(datetime.now(pytz.utc) - Mail.time <= timedelta(days=7)).count()

    def mail_last_30_days(self, obj):
        return Mail.query.filter(datetime.now(pytz.utc) - Mail.time <= timedelta(days=30)).count()

    def mail_total(self, obj):
        return Mail.query.count()


class AdminStatisticsMailDetail(ResourceDetail):
    """
    Detail by id
    """
    methods = ['GET']
    decorators = (api.has_permission('is_admin'),)
    schema = AdminStatisticsMailSchema
    data_layer = {
        'class': NoModelLayer,
        'session': db.session
    }
