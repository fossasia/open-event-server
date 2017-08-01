from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.bootstrap import api
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.microlocation import Microlocation
from app.models.session import Session
from app.api.helpers.db import safe_query
from app.api.helpers.utilities import require_relationship
from app.api.helpers.permission_manager import has_access
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.query import event_query


class MicrolocationSchema(Schema):
    """
    Api schema for Microlocation Model
    """

    class Meta:
        """
        Meta class for Microlocation Api Schema
        """
        type_ = 'microlocation'
        self_view = 'v1.microlocation_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.session_list'
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    latitude = fields.Float(validate=lambda n: -90 <= n <= 90, allow_none=True)
    longitude = fields.Float(validate=lambda n: -180 <= n <= 180, allow_none=True)
    floor = fields.Integer(allow_none=True)
    room = fields.Str(allow_none=True)
    sessions = Relationship(attribute='session',
                            self_view='v1.microlocation_session',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.session_list',
                            related_view_kwargs={'microlocation_id': '<id>'},
                            schema='SessionSchema',
                            type_='session')
    event = Relationship(attribute='event',
                         self_view='v1.microlocation_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'microlocation_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class MicrolocationListPost(ResourceList):
    """
    List and create microlocations
    """
    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ForbiddenException({'source': ''}, 'Co-organizer access is required.')

    methods = ['POST', ]
    schema = MicrolocationSchema
    data_layer = {'session': db.session,
                  'model': Microlocation}


class MicrolocationList(ResourceList):
    """
    List Microlocations
    """
    def query(self, view_kwargs):
        query_ = self.session.query(Microlocation)
        query_ = event_query(self, query_, view_kwargs)
        if view_kwargs.get('session_id'):
            session = safe_query(self, Session, 'id', view_kwargs['session_id'], 'session_id')
            query_ = query_.join(Session).filter(Session.id == session.id)
        return query_

    view_kwargs = True
    methods = ['GET']
    schema = MicrolocationSchema
    data_layer = {'session': db.session,
                  'model': Microlocation,
                  'methods': {
                      'query': query
                  }}


class MicrolocationDetail(ResourceDetail):
    """
    Microlocation detail by id
    """

    def before_get_object(self, view_kwargs):

        if view_kwargs.get('session_id') is not None:
            sessions = safe_query(self, Session, 'id', view_kwargs['session_id'], 'session_id')
            if sessions.event_id is not None:
                view_kwargs['id'] = sessions.event_id
            else:
                view_kwargs['id'] = None

    decorators = (api.has_permission('is_coorganizer', methods="PATCH,DELETE", fetch="event_id", fetch_as="event_id",
                                     model=Microlocation),)
    schema = MicrolocationSchema
    data_layer = {'session': db.session,
                  'model': Microlocation,
                  'methods': {'before_get_object': before_get_object}}


class MicrolocationRelationshipRequired(ResourceRelationship):
    """
    Microlocation Relationship for required entities
    """
    decorators = (api.has_permission('is_coorganizer', methods="PATCH", fetch="event_id", fetch_as="event_id",
                                     model=Microlocation),)
    methods = ['GET', 'PATCH']
    schema = MicrolocationSchema
    data_layer = {'session': db.session,
                  'model': Microlocation}


class MicrolocationRelationshipOptional(ResourceRelationship):
    """
    Microlocation Relationship
    """
    decorators = (api.has_permission('is_coorganizer', methods="PATCH,DELETE", fetch="event_id", fetch_as="event_id",
                                     model=Microlocation),)
    schema = MicrolocationSchema
    data_layer = {'session': db.session,
                  'model': Microlocation}
