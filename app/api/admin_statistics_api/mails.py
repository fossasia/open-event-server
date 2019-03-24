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
from app.api.helpers.db import get_count


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

    def mail_last_1_day(self, obj):
        mails_till_last_1_day = Mail.query.filter(Mail.time >= datetime.now(pytz.utc) - timedelta(days=1)).count()
        return mails_till_last_1_day

    def mail_last_3_days(self, obj):
        mails_till_last_3_day = Mail.query.filter(Mail.time >= datetime.now(pytz.utc) - timedelta(days=3)).count()
        return mails_till_last_3_day

    def mail_last_7_days(self, obj):
        mails_till_last_7_day = Mail.query.filter(Mail.time >= datetime.now(pytz.utc) - timedelta(days=7)).count()
        return mails_till_last_7_day

    def mail_last_30_days(self, obj):
        mails_till_last_30_day = Mail.query.filter(Mail.time >= datetime.now(pytz.utc) - timedelta(days=30)).count()
        return mails_till_last_30_day


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
