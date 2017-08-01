from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.sponsor import Sponsor
from app.api.bootstrap import api
from app.api.helpers.utilities import require_relationship
from app.api.helpers.permission_manager import has_access
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.query import event_query


class SponsorSchema(Schema):
    """
    Sponsors API schema based on Sponsors model
    """

    class Meta:
        """
        Meta class for Sponsor schema
        """
        type_ = 'sponsor'
        self_view = 'v1.sponsor_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    url = fields.Url(allow_none=True)
    level = fields.Integer(allow_none=True)
    logo_url = fields.Url(allow_none=True)
    type = fields.Str(allow_none=True)
    event = Relationship(attribute='event',
                         self_view='v1.sponsor_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'sponsor_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class SponsorListPost(ResourceList):
    """
    List and create Sponsors
    """
    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ForbiddenException({'source': ''}, 'Co-organizer access is required.')

    methods = ['POST']
    schema = SponsorSchema
    data_layer = {'session': db.session,
                  'model': Sponsor}


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
        query_ = event_query(self, query_, view_kwargs)
        return query_

    view_kwargs = True
    methods = ['GET']
    schema = SponsorSchema
    data_layer = {'session': db.session,
                  'model': Sponsor,
                  'methods': {
                      'query': query
                  }}


class SponsorDetail(ResourceDetail):
    """
    Sponsor detail by id
    """
    decorators = (api.has_permission('is_coorganizer', methods="PATCH,DELETE", fetch="event_id", fetch_as="event_id",
                                     model=Sponsor),)
    schema = SponsorSchema
    data_layer = {'session': db.session,
                  'model': Sponsor}


class SponsorRelationship(ResourceRelationship):
    """
    Sponsor Schema Relation
    """
    decorators = (api.has_permission('is_coorganizer', methods="PATCH,DELETE", fetch="event_id", fetch_as="event_id",
                                     model=Sponsor),)
    methods = ['GET', 'PATCH']
    schema = SponsorSchema
    data_layer = {'session': db.session,
                  'model': Sponsor}
