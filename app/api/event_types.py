from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound

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
    slug = fields.Str(dump_only=True)
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
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('event_identifier'):
            try:
                event = self.session.query(Event).filter_by(identifier=view_kwargs['event_identifier']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_identifier'},
                                     "Event: {} not found".format(view_kwargs['event_identifier']))
            else:
                view_kwargs['event_id'] = event.id

        if view_kwargs.get('event_id'):
            try:
                event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_id'},
                                     "Event: {} not found".format(view_kwargs['event_id']))
            else:
                if event.event_type_id:
                    view_kwargs['id'] = event.event_type_id
                else:
                    view_kwargs['id'] = None

    decorators = (jwt_required, api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = EventTypeSchema
    data_layer = {'session': db.session,
                  'model': EventType,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


class EventTypeRelationship(ResourceRelationship):
    """
    Event type Relationship
    """
    decorators = (jwt_required, )
    schema = EventTypeSchema
    data_layer = {'session': db.session,
                  'model': EventType}
