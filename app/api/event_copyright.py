from datetime import datetime
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.event_copyright import EventCopyright
from app.models.event import Event


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

    def query(self, view_kwargs):
        query_ = self.session.query(EventCopyright)
        if view_kwargs.get('id'):
            query_ = query_.join(Event).filter(Event.id == view_kwargs['id'])
        elif view_kwargs.get('identifier'):
            query_ = query_.join(Event).filter(Event.identifier == view_kwargs['identifier'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('id'):
            event = self.session.query(Event).filter_by(id=view_kwargs['id']).one()
            data['event_id'] = event.id
        elif view_kwargs.get('identifier'):
            event = self.session.query(Event).filter_by(identifier=view_kwargs['identifier']).one()
            data['event_id'] = event.id

    view_kwargs = True
    decorators = (jwt_required, )
    schema = EventCopyrightSchema
    data_layer = {'session': db.session,
                  'model': EventCopyright,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class EventCopyrightDetail(ResourceDetail):
    decorators = (jwt_required, )
    schema = EventCopyrightSchema
    data_layer = {'session': db.session,
                  'model': EventCopyright}


class EventCopyrightRelationship(ResourceRelationship):
    decorators = (jwt_required, )
    schema = EventCopyrightSchema
    data_layer = {'session': db.session,
                  'model': EventCopyright}
