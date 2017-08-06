from flask_rest_jsonapi import ResourceDetail
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields
from datetime import datetime
import pytz

from app.api.helpers.utilities import dasherize
from app.api.bootstrap import api
from app.models import db
from app.models.event import Event
from app.api.data_layers.NoModelLayer import NoModelLayer


class AdminStatisticsEventSchema(Schema):
    """
    Api schema
    """
    class Meta:
        """
        Meta class
        """
        type_ = 'admin-statistics-event'
        self_view = 'v1.admin_statistics_event_detail'
        inflect = dasherize

    id = fields.String()
    draft = fields.Method("events_draft_count")
    published = fields.Method("events_published_count")
    past = fields.Method("events_past_count")
    total = fields.Method("events_total_count")

    def events_draft_count(self, obj):
        return Event.query.filter_by(state='draft').count()

    def events_published_count(self, obj):
        return Event.query.filter_by(state='published').count()

    def events_past_count(self, obj):
        return Event.query.filter(Event.ends_at < datetime.now(pytz.utc)).count()

    def events_total_count(self, obj):
        return Event.query.count()


class AdminStatisticsEventDetail(ResourceDetail):
    """
    Detail by id
    """
    methods = ['GET']
    decorators = (api.has_permission('is_admin'),)
    schema = AdminStatisticsEventSchema
    data_layer = {
        'class': NoModelLayer,
        'session': db.session
    }
