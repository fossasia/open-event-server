from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from marshmallow import validates_schema
import marshmallow.validate as validate

from app.api.helpers.utilities import dasherize
from app.models import db
from app.api.helpers.permissions import jwt_required
from app.models.event import Event
from app.models.call_for_paper import CallForPaper
from app.api.helpers.exceptions import UnprocessableEntity


class CallForPaperSchema(Schema):
    """
    Api Schema for cfp model
    """
    class Meta:
        """
        Meta class for cfp Api Schema
        """
        type_ = 'call-for-paper'
        self_view = 'v1.call_for_paper_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @validates_schema
    def validate_date(self, data):
        if data['starts_at'] >= data['ends_at']:
            raise UnprocessableEntity({'pointer': '/data/attributes/ends-at'}, "ends-at should be after starts-at")

    id = fields.Str(dump_only=True)
    announcement = fields.Str(required=True)
    starts_at = fields.DateTime(required=True)
    ends_at = fields.DateTime(required=True)
    hash = fields.Str()
    privacy = fields.String(validate=validate.OneOf(choices=["private", "public"]))
    event = Relationship(attribute='event',
                         self_view='v1.call_for_paper_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'call_for_paper_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class CallForPaperList(ResourceList):
    """
    List and create cfp
    """

    def query(self, view_kwargs):
        query_ = self.session.query(CallForPaper)
        if view_kwargs.get('id'):
            query_ = query_.join(Event).filter(Event.id == view_kwargs['id'])
        elif view_kwargs.get('identifier'):
            query_ = query_.join(Event).filter(Event.identifier == view_kwargs['identifier'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('id'):
            event = self.session.query(Event).filter_by(id=view_kwargs['id']).one()
            data['event_id'] = event.id
        elif view_kwargs.get('identifier'):
            event = self.session.query(Event).filter_by(identifier=view_kwargs['identifier']).one()
            data['event_id'] = event.id

    view_kwargs = True
    decorators = (jwt_required, )
    schema = CallForPaperSchema
    data_layer = {'session': db.session,
                  'model': CallForPaper,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class CallForPaperDetail(ResourceDetail):
    """
    cfs detail by id
    """
    def query(self, view_kwargs):
        query_ = self.session.query(CallForPaper)
        if view_kwargs.get('id'):
            query_ = query_.join(Event).filter(Event.id == view_kwargs['id'])
        elif view_kwargs.get('identifier'):
            query_ = query_.join(Event).filter(Event.identifier == view_kwargs['identifier'])
        return query_

    decorators = (jwt_required,)
    schema = CallForPaperSchema
    data_layer = {'session': db.session,
                  'model': CallForPaper,
                  'methods': {
                      'query': query
                  }}


class CallForPaperRelationship(ResourceRelationship):
    """
    cfs Relationship
    """
    decorators = (jwt_required,)
    schema = CallForPaperSchema
    data_layer = {'session': db.session,
                  'model': CallForPaper}
