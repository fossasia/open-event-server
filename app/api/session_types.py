from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound
from datetime import datetime
from marshmallow import validates_schema

from app.api.helpers.utilities import dasherize
from app.models import db
from app.api.helpers.permissions import jwt_required
from app.models.session_type import SessionType
from app.models.event import Event
from app.models.session import Session
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.bootstrap import api


class SessionTypeSchema(Schema):
    """
    Api Schema for session type model
    """
    class Meta:
        """
        Meta class for SessionTypeSchema
        """
        type_ = 'session-type'
        self_view = 'v1.session_type_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @validates_schema
    def validate_length(self, data):
        try:
            datetime.strptime(data['length'], '%H:%M')
        except ValueError:
            raise UnprocessableEntity({'pointer': '/data/attributes/length'}, "Length should be in the format %H:%M")

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    length = fields.Str(required=True)
    event = Relationship(attribute='event',
                         self_view='v1.session_type_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'session_type_id': '<id>'},
                         schema='EventSchema',
                         type_='event')
    sessions = Relationship(attribute='session',
                            self_view='v1.session_type_sessions',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.session_list',
                            related_view_kwargs={'session_type_id': '<id>'},
                            schema='SessionSchema',
                            many=True,
                            type_='session')


class SessionTypeList(ResourceList):
    """
    List and create sessions
    """

    def query(self, view_kwargs):
        """
        query method for Session Type List
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(SessionType)
        if view_kwargs.get('event_id'):
            try:
                event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_id'},
                                     "Event: {} not found".format(view_kwargs['event_id']))
            else:
                query_ = query_.join(Event).filter(Event.id == event.id)
        elif view_kwargs.get('event_identifier'):
            query_ = query_.join(Event).filter(Event.identifier == view_kwargs['event_identifier'])
            try:
                event = self.session.query(Event).filter_by(identifier=view_kwargs['event_identifier']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_identifier'},
                                     "Event: {} not found".format(view_kwargs['event_identifier']))
            else:
                query_ = query_.join(Event).filter(Event.id == event.id)
        return query_

    def before_create_object(self, data, view_kwargs):
        """
        method to create object before post
        :param data:
        :param view_kwargs:
        :return:
        """
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
    decorators = (api.has_permission('is_coorganizer', fetch='event_id', fetch_as="event_id", methods="POST",
                                     check=lambda a: a.get('event_id') or a.get('event_identifier')),)
    schema = SessionTypeSchema
    data_layer = {'session': db.session,
                  'model': SessionType,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class SessionTypeDetail(ResourceDetail):
    """
    Detail about a single session type by id
    """

    def before_get_object(self, view_kwargs):
        """
        before get method for session type detail
        :param data:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('session_id'):
            try:
                session = self.session.query(Session).filter_by(id=view_kwargs['session_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'session_id'},
                                     "Session: {} not found".format(view_kwargs['session_id']))
            else:
                if session.session_type_id:
                    view_kwargs['id'] = session.session_type_id
                else:
                    view_kwargs['id'] = None

    decorators = (api.has_permission('is_coorganizer', methods="PATCH,DELETE", fetch="event_id", fetch_as="event_id",
                                     model=SessionType, check=lambda a: a.get('id') is not None),)
    schema = SessionTypeSchema
    data_layer = {'session': db.session,
                  'model': SessionType,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


class SessionTypeRelationship(ResourceRelationship):
    """
    SessionType Relationship
    """
    decorators = (jwt_required,)
    schema = SessionTypeSchema
    data_layer = {'session': db.session,
                  'model': SessionType}
