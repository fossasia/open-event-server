from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from marshmallow import validates_schema
import marshmallow.validate as validate
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.utilities import dasherize
from app.models import db
from app.api.helpers.permissions import jwt_required
from app.models.event import Event
from app.api.helpers.exceptions import UnprocessableEntity
from app.models.speakers_call import SpeakersCall


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
    hash = fields.Str()
    privacy = fields.String(validate=validate.OneOf(choices=["private", "public"]))
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
    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('event_id'):
            try:
                event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_id'},
                                     "Event: {} not found".format(view_kwargs['event_id']))
            else:
                data['event_id'] = event.id
        elif view_kwargs.get('event_identifier'):
            try:
                event = self.session.query(Event).filter_by(identifier=view_kwargs['event_identifier']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_identifier'},
                                     "Event: {} not found".format(view_kwargs['event_identifier']))
            else:
                data['event_id'] = event.id

    view_kwargs = True
    decorators = (jwt_required, )
    schema = SpeakersCallSchema
    methods = ['POST', ]
    data_layer = {'session': db.session,
                  'model': SpeakersCall,
                  'methods': {
                      'before_create_object': before_create_object
                  }}


class SpeakersCallDetail(ResourceDetail):
    """
     speakers call detail by id
    """
    def before_get_object(self, view_kwargs):
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
                event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_id'},
                                     "Event: {} not found".format(view_kwargs['event_id']))
            else:
                if event.speakers_call:
                    view_kwargs['id'] = event.speakers_call.id
                else:
                    view_kwargs['id'] = None

    decorators = (jwt_required,)
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
    decorators = (jwt_required,)
    schema = SpeakersCallSchema
    data_layer = {'session': db.session,
                  'model': SpeakersCall}
