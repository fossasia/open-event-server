from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.social_link import SocialLink
from app.api.bootstrap import api
from app.api.helpers.utilities import require_relationship
from app.api.helpers.query import event_query


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
        query_ = event_query(self, query_, view_kwargs)
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
                                     model=SocialLink),)
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
