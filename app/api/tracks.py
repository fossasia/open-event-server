from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.track import Track
from app.models.session import Session
from app.models.event import Event


class TrackSchema(Schema):
    """
    Api Schema for track model
    """
    class Meta:
        """
        Meta class for User Api Schema
        """
        type_ = 'track'
        self_view = 'v1.track_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    track_image_url = fields.Str()
    color = fields.Str()
    location = fields.Str()
    event = Relationship(attribute='event',
                         self_view='v1.track_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'track_id': '<id>'},
                         schema='EventSchema',
                         type_='event')

    sessions = Relationship(attribute='sessions',
                            self_view='v1.track_sessions',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.session_list',
                            related_view_kwargs={'track_id': '<id>'},
                            schema='SessionSchema',
                            many=True,
                            type_='session')


class TrackList(ResourceList):
    """
    List and create Tracks
    """
    def query(self, view_kwargs):
        query_ = self.session.query(Track)
        if view_kwargs.get('event_id') is not None:
            query_ = query_.join(Event).filter(Event.id == view_kwargs['event_id'])
        return query_

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('event_id') is not None:
            event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            data['event_id'] = event.id

    view_kwargs = True
    decorators = (jwt_required, )
    schema = TrackSchema
    data_layer = {'session': db.session,
                  'model': Track,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class TrackDetail(ResourceDetail):
    """
    Track detail by id
    """
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('session_id') is not None:
            try:
                session = self.session.query(Session).filter_by(id=view_kwargs['session_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'session_id'},
                                     "Session: {} not found".format(view_kwargs['session_id']))
            else:
                if session.event_id is not None:
                    view_kwargs['id'] = session.track_id
                else:
                    view_kwargs['id'] = None

    decorators = (jwt_required, )
    schema = TrackSchema
    data_layer = {'session': db.session,
                  'model': Track,
                  'methods': {'before_get_object': before_get_object}}


class TrackRelationship(ResourceRelationship):
    """
    Track Relationship
    """
    decorators = (jwt_required, )
    schema = TrackSchema
    data_layer = {'session': db.session,
                  'model': Track}
