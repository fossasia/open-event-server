from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.social_links import SocialLinkSchema
from app.models import db
from app.models.social_link import SocialLink


class SocialLinkListPost(ResourceList):
    """
    List and Create Social Links for an event
    """

    def before_post(self, args, kwargs, data):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event'], data)

    methods = ['POST']
    schema = SocialLinkSchema
    data_layer = {'session': db.session, 'model': SocialLink}


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
        query_ = event_query(query_, view_kwargs)
        return query_

    view_kwargs = True
    methods = ['GET']
    schema = SocialLinkSchema
    data_layer = {'session': db.session, 'model': SocialLink, 'methods': {'query': query}}


class SocialLinkDetail(ResourceDetail):
    """
    Social Link detail by id
    """

    decorators = (
        api.has_permission(
            'is_coorganizer',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=SocialLink,
        ),
    )
    schema = SocialLinkSchema
    data_layer = {'session': db.session, 'model': SocialLink}


class SocialLinkRelationship(ResourceRelationship):
    """
    Social Link Relationship
    """

    decorators = (
        api.has_permission(
            'is_coorganizer',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=SocialLink,
        ),
    )
    methods = ['GET', 'PATCH']
    schema = SocialLinkSchema
    data_layer = {'session': db.session, 'model': SocialLink}
