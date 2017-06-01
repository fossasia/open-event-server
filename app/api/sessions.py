from datetime import datetime
from app.api.helpers.permissions import jwt_required
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from app.models import db
from app.models.session import Session


class SessionSchema(Schema):
    """
    Api schema for Session Model
    """
    class Meta:
        """
        Meta class for Session Api Schema
        """
        type_ = 'session'
        self_view = 'v1.session_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.session_list'

    id = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    subtitle = fields.Str()
    event_url = fields.Str()
    level = fields.Str()
    short_abstract = fields.Str()
    long_abstract = fields.Str()
    comments = fields.Str()
    starts_at = fields.DateTime(required=True)
    ends_at = fields.DateTime(required=True)
    microlocation = Relationship(attribute='microlocation',
                                 self_view='v1.session_microlocation',
                                 self_view_kwargs={'id': '<id>'},
                                 related_view='v1.microlocation_detail',
                                 related_view_kwargs={'session_id': '<id>'},
                                 schema='MicrolocationSchema',
                                 type_='microlocation')


class SessionList(ResourceList):
    """
    List and create Sessions
    """
    decorators = (jwt_required, )
    schema = SessionSchema
    data_layer = {'session': db.session,
                  'model': Session}


class SessionDetail(ResourceDetail):
    """
    Session detail by id
    """
    decorators = (jwt_required, )
    schema = SessionSchema
    data_layer = {'session': db.session,
                  'model': Session}


class SessionRelationship(ResourceRelationship):
    """
    Session Relationship
    """
    decorators = (jwt_required, )
    schema = SessionSchema
    data_layer = {'session': db.session,
                  'model': Session}
