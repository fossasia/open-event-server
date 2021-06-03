from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.events import Event
from app.api.helpers.db import get_count
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permission_manager import has_access
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.sponsors import SponsorSchema
from app.models import db
from app.models.sponsor import Sponsor


class SponsorListPost(ResourceList):
    """
    List and create Sponsors
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
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ForbiddenError({'source': ''}, 'Co-organizer access is required.')
        if (
            get_count(
                db.session.query(Event).filter_by(
                    id=int(data['event']), is_sponsors_enabled=False
                )
            )
            > 0
        ):
            raise ForbiddenError({'pointer': ''}, "Sponsors are disabled for this Event")

    methods = ['POST']
    schema = SponsorSchema
    data_layer = {'session': db.session, 'model': Sponsor}


class SponsorList(ResourceList):
    """
    List Sponsors
    """

    def query(self, view_kwargs):
        """
        query method for Sponsor List
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(Sponsor)
        query_ = event_query(query_, view_kwargs)
        return query_

    view_kwargs = True
    methods = ['GET']
    schema = SponsorSchema
    data_layer = {'session': db.session, 'model': Sponsor, 'methods': {'query': query}}


class SponsorDetail(ResourceDetail):
    """
    Sponsor detail by id
    """

    decorators = (
        api.has_permission(
            'is_coorganizer',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=Sponsor,
        ),
    )
    schema = SponsorSchema
    data_layer = {'session': db.session, 'model': Sponsor}


class SponsorRelationship(ResourceRelationship):
    """
    Sponsor Schema Relation
    """

    decorators = (
        api.has_permission(
            'is_coorganizer',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=Sponsor,
        ),
    )
    methods = ['GET', 'PATCH']
    schema = SponsorSchema
    data_layer = {'session': db.session, 'model': Sponsor}
