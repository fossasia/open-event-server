from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from app.models import db
from app.api.helpers.permissions import jwt_required
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound
from app.models.event import Event
from app.models.call_for_paper import CallForPaper
import pytz
from datetime import datetime
import dateutil.parser


class CallForPaperSchema(Schema):
    """
    Api Schema for cfp model
    """
    class Meta:
        """
        Meta class for cfp Api Schema
        """
        type_ = 'call_for_paper'
        self_view = 'v1.call_for_paper_detail'
        self_view_kwargs = {'id': '<id>'}

    id = fields.Str(dump_only=True)
    announcement = fields.Str(required=True)
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)
    timezone = fields.Str(default="UTC")
    hash = fields.Str()
    privacy = fields.String()
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
        if view_kwargs.get('event_id') is not None:
            query_ = query_.join(Event).filter(Event.id == view_kwargs['event_id'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('event_id') is not None:
            event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            data['event_id'] = event.id

    def after_get(self, result):
        tz = pytz.timezone(result['data'][0]['attributes']['timezone'])
        start_date_str = result['data'][0]['attributes']['start_date']
        start_date_datetime = dateutil.parser.parse(start_date_str)
        start_date_datetime = tz.localize(start_date_datetime.replace(tzinfo=None))
        result['data'][0]['attributes']['start_date'] = start_date_datetime.isoformat()
        end_date_str = result['data'][0]['attributes']['end_date']
        end_date_datetime = dateutil.parser.parse(end_date_str)
        end_date_datetime = tz.localize(end_date_datetime.replace(tzinfo=None))
        result['data'][0]['attributes']['end_date'] = end_date_datetime.isoformat()

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

    def after_get(self, result):
        tz = pytz.timezone(result['data']['attributes']['timezone'])
        start_date_str = result['data']['attributes']['start_date']
        start_date_datetime = dateutil.parser.parse(start_date_str)
        start_date_datetime = tz.localize(start_date_datetime.replace(tzinfo=None))
        result['data']['attributes']['start_date'] = start_date_datetime.isoformat()
        end_date_str = result['data']['attributes']['end_date']
        end_date_datetime = dateutil.parser.parse(end_date_str)
        end_date_datetime = tz.localize(end_date_datetime.replace(tzinfo=None))
        result['data']['attributes']['end_date'] = end_date_datetime.isoformat()

    decorators = (jwt_required,)
    schema = CallForPaperSchema
    data_layer = {'session': db.session,
                  'model': CallForPaper}


class CallForPaperRelationship(ResourceRelationship):
    """
    cfs Relationship
    """
    decorators = (jwt_required,)
    schema = CallForPaperSchema
    data_layer = {'session': db.session,
                  'model': CallForPaper}
