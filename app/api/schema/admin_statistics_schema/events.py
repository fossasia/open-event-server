from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields
from app.models.event import Event
from app.api.helpers.db import get_count
from app.api.helpers.utilities import dasherize
from datetime import datetime
import pytz


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

    def events_draft_count(self, obj):
        events = Event.query.filter(Event.ends_at > datetime.now(pytz.utc))
        return get_count(events.filter_by(state='draft', deleted_at=None))

    def events_published_count(self, obj):
        events = Event.query.filter(Event.ends_at > datetime.now(pytz.utc))
        return get_count(events.filter_by(state='published', deleted_at=None))

    def events_past_count(self, obj):
        return get_count(Event.query.filter(Event.ends_at < datetime.now(pytz.utc)))
