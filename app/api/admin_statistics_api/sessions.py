from flask_rest_jsonapi import ResourceDetail
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.api.bootstrap import api
from app.models import db
from app.models.session import Session
from app.api.data_layers.NoModelLayer import NoModelLayer
from app.api.helpers.db import get_count


class AdminStatisticsSessionSchema(Schema):
    """
    Api schema
    """
    class Meta:
        """
        Meta class
        """
        type_ = 'admin-statistics-session'
        self_view = 'v1.admin_statistics_session_detail'
        inflect = dasherize

    id = fields.String()
    draft = fields.Method("sessions_draft_count")
    submitted = fields.Method("sessions_submitted_count")
    accepted = fields.Method("sessions_accepted_count")
    confirmed = fields.Method("sessions_confirmed_count")
    pending = fields.Method("sessions_pending_count")
    rejected = fields.Method("sessions_rejected_count")

    def sessions_draft_count(self, obj):
        return get_count(Session.query.filter_by(state='draft'))

    def sessions_submitted_count(self, obj):
        return get_count(Session.query.filter_by(state='submitted'))

    def sessions_accepted_count(self, obj):
        return get_count(Session.query.filter_by(state='accepted'))

    def sessions_confirmed_count(self, obj):
        return get_count(Session.query.filter_by(state='confirmed'))

    def sessions_pending_count(self, obj):
        return get_count(Session.query.filter_by(state='pending'))

    def sessions_rejected_count(self, obj):
        return get_count(Session.query.filter_by(state='rejected'))


class AdminStatisticsSessionDetail(ResourceDetail):
    """
    Detail by id
    """
    methods = ['GET']
    decorators = (api.has_permission('is_admin'),)
    schema = AdminStatisticsSessionSchema
    data_layer = {
        'class': NoModelLayer,
        'session': db.session
    }
