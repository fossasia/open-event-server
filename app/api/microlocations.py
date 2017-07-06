from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.bootstrap import api
from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.microlocation import Microlocation
from app.models.session import Session
from app.models.event import Event


class MicrolocationSchema(Schema):
    """
    Api schema for Microlocation Model
    """

    class Meta:
        """
        Meta class for Microlocation Api Schema
        """
        type_ = 'microlocation'
        self_view = 'v1.microlocation_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.session_list'
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    latitude = fields.Float(validate=lambda n: -90 <= n <= 90, allow_none=True)
    longitude = fields.Float(validate=lambda n: -180 <= n <= 180, allow_none=True)
    floor = fields.Integer(allow_none=True)
    room = fields.Str(allow_none=True)
    sessions = Relationship(attribute='session',
                            self_view='v1.microlocation_session',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.session_list',
                            related_view_kwargs={'microlocation_id': '<id>'},
                            schema='SessionSchema',
                            type_='session')
    event = Relationship(attribute='event',
                         self_view='v1.microlocation_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'microlocation_id': '<id>'},
                         schema='EventSchema',
                         type_='event')


class MicrolocationList(ResourceList):
    """
    List and create Microlocations
    """

    def query(self, view_kwargs):
        query_ = self.session.query(Microlocation)
        if view_kwargs.get('event_id'):
            query_ = query_.join(Event).filter(Event.id == view_kwargs['event_id'])
        elif view_kwargs.get('event_identifier'):
            query_ = query_.join(Event).filter(Event.identifier == view_kwargs['event_identifier'])
        if view_kwargs.get('session_id'):
            query_ = query_.join(Session).filter(Session.id == view_kwargs['session_id'])
        return query_

    def before_create_object(self, data, view_kwargs):
        # Permsission Manager ensures that there is event_id if any event_identifier is provided
        # and throws 404 if event is not found
        event = self.session.query(Event).filter_by(id=view_kwargs['event_id']).one()
        data['event_id'] = event.id

    view_kwargs = True
    decorators = (api.has_permission('is_coorganizer', fetch='event_id', fetch_as="event_id", methods="POST",
                  check=lambda a: a.get('event_id') or a.get('event_identifier')),)
    schema = MicrolocationSchema
    data_layer = {'session': db.session,
                  'model': Microlocation,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class MicrolocationDetail(ResourceDetail):
    """
    Microlocation detail by id
    """

    def before_get_object(self, view_kwargs):

        if view_kwargs.get('session_id') is not None:
            try:
                sessions = self.session.query(Session).filter_by(
                    id=view_kwargs['session_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'session_id'},
                                     "Session: {} not found".format(view_kwargs['session_id']))
            else:
                if sessions.event_id is not None:
                    view_kwargs['id'] = sessions.event_id
                else:
                    view_kwargs['id'] = None

    decorators = (api.has_permission('is_coorganizer', methods="PATCH,DELETE", fetch="event_id", fetch_as="event_id",
                                     model=Microlocation, check=lambda a: a.get('id') is not None),)
    schema = MicrolocationSchema
    data_layer = {'session': db.session,
                  'model': Microlocation,
                  'methods': {'before_get_object': before_get_object}}


class MicrolocationRelationship(ResourceRelationship):
    """
    Microlocation Relationship
    """
    decorators = (jwt_required,)
    schema = MicrolocationSchema
    data_layer = {'session': db.session,
                  'model': Microlocation}
