from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.event_type import EventType
from app.models.event import Event
from app.api.bootstrap import api
from app.api.helpers.permissions import is_admin, is_user_itself, jwt_required


class EventTypeSchema(Schema):
    """
    Api Schema for event type model
    """

    class Meta:
        """
        Meta class for event type Api Schema
        """
        type_ = 'event-type'
        self_view = 'v1.event_type_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    slug = fields.Str()
    events = Relationship(attribute='event',
                          self_view='v1.event_type_event',
                          self_view_kwargs={'id': '<id>'},
                          related_view='v1.event_list',
                          related_view_kwargs={'event_type_id': '<id>'},
                          many=True,
                          schema='EventSchema',
                          type_='event')

class EventTypeList(ResourceList):

    """
    List and create event types
    """
    decorators = (jwt_required, api.has_permission('is_admin', methods="POST"),)
    schema = EventTypeSchema
    data_layer = {'session': db.session,
                  'model': EventType}


class EventTypeDetail(ResourceDetail):
    """
    Event type detail by id
    """
    decorators = (jwt_required, api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = EventTypeSchema
    data_layer = {'session': db.session,
                  'model': EventType}


class EventTypeRelationship(ResourceRelationship):
    """
    Event type Relationship
    """
    decorators = (jwt_required, )
    schema = EventTypeSchema
    data_layer = {'session': db.session,
                  'model': EventType}
