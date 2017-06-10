from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.social_link import SocialLink
from app.models.event import Event


class SocialLinkSchema(Schema):

    class Meta:
        type_ = 'social_link'
        self_view = 'v1.social_link_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    link = fields.Url(required=True)
    event = Relationship(attribute='event',
                         self_view='v1.social_link_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'social_link_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class SocialLinkList(ResourceList):

    def query(self, view_kwargs):
        query_ = self.session.query(SocialLink)
        if view_kwargs.get('id') is not None:
            query_ = query_.join(Event).filter(Event.id == view_kwargs['id'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('id') is not None:
            event = self.session.query(Event).filter_by(id=view_kwargs['id']).one()
            data['event_id'] = event.id

    view_kwargs = True
    decorators = (jwt_required, )
    schema = SocialLinkSchema
    data_layer = {'session': db.session,
                  'model': SocialLink,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class SocialLinkDetail(ResourceDetail):
    decorators = (jwt_required, )
    schema = SocialLinkSchema
    data_layer = {'session': db.session,
                  'model': SocialLink}


class SocialLinkRelationship(ResourceRelationship):
    decorators = (jwt_required, )
    schema = SocialLinkSchema
    data_layer = {'session': db.session,
                  'model': SocialLink}
