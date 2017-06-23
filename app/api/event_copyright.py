from datetime import datetime
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.bootstrap import api
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
    holder = fields.Str()
    holder_url = fields.Url()
    licence = fields.Str(required=True)
    licence_url = fields.Url()
    year = fields.Int(validate=lambda n: 1900 <= n <= datetime.now().year)
    logo_url = fields.Url(attribute='logo')
    event = Relationship(attribute='event',
                         self_view='v1.copyright_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'copyright_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class EventCopyrightList(ResourceList):
    def before_create_object(self, data, view_kwargs):

        # Permission Manager will ensure that event_id is fetched into
        # view_kwargs from event_identifier
        try:
            event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
        except NoResultFound:
            raise ObjectNotFound({'parameter': 'event_identifier'},
                                 'Event: {} not found'.format(view_kwargs['event_id']))
        else:
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

    def before_patch(self, args, kwargs):
        if kwargs.get('event_id'):
            try:
                event_copyright = EventCopyright.query.filter_by(event_id=kwargs['event_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event identifier'}, "Object: not found")
            kwargs['id'] = event_copyright.id


    def before_get_object(self, view_kwargs):
        # Permission Manager is not used for GET requests so need to fetch here the event ID 
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
                event_copyright = self.session.query(EventCopyright).filter_by(event_id=view_kwargs['event_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event identifier'}, "Object: not found")
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
