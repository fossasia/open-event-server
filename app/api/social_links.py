from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.social_link import SocialLink
from app.models.event import Event
from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.utilities import require_relationship


class SocialLinkSchema(Schema):
    """
    Social Link API Schema based on Social link model
    """
    class Meta:
        """
        Meta class for social link schema
        """
        type_ = 'social-link'
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
    """
    List and Create Social Links for an event
    """
    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)

    def query(self, view_kwargs):
        """
        query method for social link
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(SocialLink)
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            query_ = query_.join(Event).filter(Event.id == event.id)
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'identifier')
            query_ = query_.join(Event).filter(Event.id == event.id)
        return query_

    def before_create_object(self, data, view_kwargs):
        """
        method to create object before post
        :param data:
        :param view_kwargs:
        :return:
        """
        event = None
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
        if event:
            data['event_id'] = event.id

    view_kwargs = True
    decorators = (api.has_permission('is_coorganizer', fetch='event_id', fetch_as="event_id", methods="POST",
                                     check=lambda a: a.get('event_id') or a.get('event_identifier')),)
    schema = SocialLinkSchema
    data_layer = {'session': db.session,
                  'model': SocialLink,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class SocialLinkDetail(ResourceDetail):
    """
    Social Link detail by id
    """
    decorators = (api.has_permission('is_coorganizer', methods="PATCH,DELETE", fetch="event_id", fetch_as="event_id",
                                     model=SocialLink, check=lambda a: a.get('id') is not None),)
    schema = SocialLinkSchema
    data_layer = {'session': db.session,
                  'model': SocialLink}


class SocialLinkRelationship(ResourceRelationship):
    """
    Social Link Relationship
    """
    decorators = (api.has_permission('is_coorganizer', methods="PATCH,DELETE", fetch="event_id", fetch_as="event_id",
                                     model=SocialLink),)
    methods = ['GET', 'PATCH']
    schema = SocialLinkSchema
    data_layer = {'session': db.session,
                  'model': SocialLink}
