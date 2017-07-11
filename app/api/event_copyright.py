from datetime import datetime
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.event_copyright import EventCopyright
from app.models.event import Event
from app.api.helpers.exceptions import UnprocessableEntity


class EventCopyrightSchema(Schema):

    class Meta:
        type_ = 'event-copyright'
        self_view = 'v1.event_copyright_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    holder = fields.Str(allow_none=True)
    holder_url = fields.Url(allow_none=True)
    licence = fields.Str(required=True)
    licence_url = fields.Url(allow_none=True)
    year = fields.Int(validate=lambda n: 1900 <= n <= datetime.now().year, allow_none=True)
    logo_url = fields.Url(attribute='logo', allow_none=True)
    event = Relationship(attribute='event',
                         self_view='v1.copyright_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'copyright_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class EventCopyrightList(ResourceList):

    def before_create_object(self, data, view_kwargs):
        event = None
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
        if event:
            data['event_id'] = event.id

        try:
            self.session.query(EventCopyright).filter_by(event_id=data['event_id']).one()
        except NoResultFound:
            pass
        else:
            raise UnprocessableEntity({'parameter': 'event_identifier'},
                                      "Event Copyright already exists for the provided Event ID")

    methods = ['POST', ]
    view_kwargs = True
    decorators = (api.has_permission('is_coorganizer', fetch="event_id", fetch_as="event_id"),)
    schema = EventCopyrightSchema
    data_layer = {'session': db.session,
                  'model': EventCopyright,
                  'methods': {
                      'before_create_object': before_create_object
                  }}


class EventCopyrightDetail(ResourceDetail):

    def before_patch(self, args, kwargs, data):
        event = None
        if kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', kwargs['event_id'], 'event_id')
        elif kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', kwargs['event_identifier'], 'event_identifier')

        if event:
            event_copyright = safe_query(self, EventCopyright, 'event_id', event.id, 'event_id')
            kwargs['id'] = event_copyright.id

    def before_get_object(self, view_kwargs):
        event = None
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')

        if event:
            event_copyright = safe_query(self, EventCopyright, 'event_id', event.id, 'event_id')
            view_kwargs['id'] = event_copyright.id

    decorators = (api.has_permission('is_coorganizer', fetch="event_id", fetch_as="event_id",
                                     model=EventCopyright, methods="PATCH,DELETE"),)
    schema = EventCopyrightSchema
    data_layer = {'session': db.session,
                  'model': EventCopyright,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


class EventCopyrightRelationship(ResourceRelationship):
    decorators = (jwt_required,)
    schema = EventCopyrightSchema
    data_layer = {'session': db.session,
                  'model': EventCopyright}
