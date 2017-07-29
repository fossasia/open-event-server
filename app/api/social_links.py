from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from flask_rest_jsonapi.exceptions import ObjectNotFound
from flask import request

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.social_link import SocialLink
from app.models.event import Event
from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.utilities import require_relationship
from app.api.helpers.permission_manager import has_access


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


class SocialLinkListPost(ResourceList):
    """
    List and Create Social Links for an event
    """
    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)

    methods = ['POST']
    schema = SocialLinkSchema
    data_layer = {'session': db.session,
                  'model': SocialLink}


class SocialLinkList(ResourceList):
    """
    List and Create Social Links for an event
    """
    def query(self, view_kwargs):
        """
        query method for social link
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(SocialLink)
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            if event.state != 'published':
                if 'Authorization' in request.headers and has_access('is_coorganizer', event_id=event.id):
                    query_ = query_.join(Event).filter(Event.id == event.id)
                else:
                    raise ObjectNotFound({'parameter': 'event_id'},
                                         "Event: {} not found".format(view_kwargs['event_identifier']))
            else:
                query_ = query_.join(Event).filter(Event.id == event.id)
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            if event.state != 'published':
                if 'Authorization' in request.headers and has_access('is_coorganizer', event_id=event.id):
                    query_ = query_.join(Event).filter(Event.id == event.id)
                else:
                    raise ObjectNotFound({'parameter': 'event_identifier'},
                                         "Event: {} not found".format(view_kwargs['event_identifier']))
            else:
                query_ = query_.join(Event).filter(Event.id == event.id)
        return query_

    view_kwargs = True
    methods = ['GET']
    schema = SocialLinkSchema
    data_layer = {'session': db.session,
                  'model': SocialLink,
                  'methods': {
                      'query': query
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
    decorators = (jwt_required, )
    methods = ['GET', 'PATCH']
    schema = SocialLinkSchema
    data_layer = {'session': db.session,
                  'model': SocialLink}
