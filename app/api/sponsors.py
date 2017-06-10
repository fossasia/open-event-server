from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.sponsor import Sponsor
from app.models.event import Event


class SponsorSchema(Schema):

    class Meta:
        type_ = 'sponsor'
        self_view = 'v1.sponsor_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    url = fields.Url()
    level = fields.Str()
    logo_url = fields.Url()
    type = fields.Str()
    event = Relationship(attribute='event',
                         self_view='v1.sponsor_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'sponsor_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class SponsorList(ResourceList):

    def query(self, view_kwargs):
        query_ = self.session.query(Sponsor)
        if view_kwargs.get('event_id') is not None:
            query_ = query_.join(Event).filter(Event.id == view_kwargs['event_id'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('event_id') is not None:
            event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            data['event_id'] = event.id

    decorators = (jwt_required, )
    schema = SponsorSchema
    data_layer = {'session': db.session,
                  'model': Sponsor,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class SponsorRelationship(ResourceRelationship):

    decorators = (jwt_required, )
    schema = SponsorSchema
    data_layer = {'session': db.session,
                  'model': Sponsor}


class SponsorDetail(ResourceDetail):

    decorators = (jwt_required, )
    schema = SponsorSchema
    data_layer = {'session': db.session,
                  'model': Sponsor}
