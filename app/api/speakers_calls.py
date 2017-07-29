from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from marshmallow import validates_schema
import marshmallow.validate as validate
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.bootstrap import api
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.event import Event
from app.api.helpers.exceptions import UnprocessableEntity
from app.models.speakers_call import SpeakersCall
from app.api.helpers.utilities import require_relationship
from app.api.helpers.permission_manager import has_access
from app.api.helpers.exceptions import ForbiddenException


class SpeakersCallSchema(Schema):
    """
    Api Schema for Speakers Call model
    """
    class Meta:
        """
        Meta class for Speakers Call Api Schema
        """
        type_ = 'speakers-call'
        self_view = 'v1.speakers_call_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @validates_schema(pass_original=True)
    def validate_date(self, data, original_data):
        if 'id' in original_data['data']:
            speakers_calls = SpeakersCall.query.filter_by(id=original_data['data']['id']).one()

            if 'starts_at' not in data:
                data['starts_at'] = speakers_calls.starts_at

            if 'ends_at' not in data:
                data['ends_at'] = speakers_calls.ends_at

        if data['starts_at'] >= data['ends_at']:
            raise UnprocessableEntity({'pointer': '/data/attributes/ends-at'}, "ends-at should be after starts-at")

    id = fields.Str(dump_only=True)
    announcement = fields.Str(required=True)
    starts_at = fields.DateTime(required=True)
    ends_at = fields.DateTime(required=True)
    hash = fields.Str(allow_none=True)
    privacy = fields.String(validate=validate.OneOf(choices=["private", "public"]), allow_none=True)
    event = Relationship(attribute='event',
                         self_view='v1.speakers_call_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'speakers_call_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class SpeakersCallList(ResourceList):
    """
    create Speakers Call
    """
    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ForbiddenException({'source': ''}, 'Co-organizer access is required.')

    schema = SpeakersCallSchema
    methods = ['POST', ]
    data_layer = {'session': db.session,
                  'model': SpeakersCall}


class SpeakersCallDetail(ResourceDetail):
    """
     speakers call detail by id
    """
    def before_patch(self, args, kwargs, data):
        if kwargs.get('event_id'):
            try:
                speakers_call = SpeakersCall.query.filter_by(event_id=kwargs['event_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'source': ''}, "Object: not found")
            kwargs['id'] = speakers_call.id

    def before_get_object(self, view_kwargs):
        # Permission Manager is not used for GET requests so need to fetch here the event ID
        if view_kwargs.get('event_identifier'):
            try:
                event = self.session.query(Event).filter_by(identifier=view_kwargs['event_identifier']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_identifier'},
                                     "Event: {} not found".format(view_kwargs['event_identifier']))
            else:
                view_kwargs['event_id'] = event.id

        if view_kwargs.get('event_id'):
            try:
                speakers_call = self.session.query(SpeakersCall).filter_by(event_id=view_kwargs['event_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_identifier'}, "Object: not found")
            view_kwargs['id'] = speakers_call.id

    decorators = (api.has_permission('is_coorganizer', fetch="event_id", fetch_as="event_id",
                                     model=SpeakersCall, methods="PATCH,DELETE"),)
    schema = SpeakersCallSchema
    data_layer = {'session': db.session,
                  'model': SpeakersCall,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


class SpeakersCallRelationship(ResourceRelationship):
    """
    speakers call Relationship
    """
    decorators = (api.has_permission('is_coorganizer', fetch="event_id", fetch_as="event_id",
                                     model=SpeakersCall, methods="PATCH,DELETE"),)
    schema = SpeakersCallSchema
    methods = ['GET', 'PATCH']
    data_layer = {'session': db.session,
                  'model': SpeakersCall}
