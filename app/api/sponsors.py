from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from flask import request

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.sponsor import Sponsor
from app.models.event import Event
from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.utilities import require_relationship
from app.api.helpers.permission_manager import has_access
from app.api.helpers.exceptions import ForbiddenException


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
    level = fields.Str(allow_none=True)
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
                                     model=Sponsor, check=lambda a: a.get('id') is not None),)
    schema = SponsorSchema
    data_layer = {'session': db.session,
                  'model': Sponsor}


class SponsorRelationship(ResourceRelationship):
    """
    Sponsor Schema Relation
    """
    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = SponsorSchema
    data_layer = {'session': db.session,
                  'model': Sponsor}
