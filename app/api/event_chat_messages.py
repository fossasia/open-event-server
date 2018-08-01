from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask import request
from flask import current_app as app

from flask_jwt import current_identity as current_user, _jwt_required
from app.models.event import Event
from app.api.helpers.db import safe_query
from app.api.helpers.permission_manager import has_access
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.utilities import require_relationship
from app.api.schema.event_chat_message import EventChatMessageSchema
from app.models import db
from app.models.event_chat_message import EventChatMessage
from app.models.speaker import Speaker


class EventChatMessageListPost(ResourceList):
    """
    Create Event Chat Messages
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

        if 'Authorization' in request.headers:
            _jwt_required(app.config['JWT_DEFAULT_REALM'])
        else:
            raise ForbiddenException({'source': ''}, 'Only Authorized Users can chat in Event Chat Room')

        data['user_id'] = current_user.id
        event = db.session.query(Event).filter_by(id=int(data['event'])).first()
        if event.state == 'draft':
            raise ForbiddenException({'source': ''}, 'Event Chat Room is open for only published events')
        speaker = db.session.query(Speaker).filter_by(event_id=event.id, user_id=current_user.id).first()
        if speaker:
            data['label'] = 'Speaker'
        elif current_user.is_organizer(event.id):
            data['label'] = 'Organizer'
        elif current_user.is_coorganizer(event.id):
            data['label'] = 'Co-organizer'
        elif current_user.is_track_organizer(event.id):
            data['label'] = 'Track Organizer'
        elif current_user.is_moderator(event.id):
            data['label'] = 'Moderator'
        elif current_user.is_registrar(event.id):
            data['label'] = 'Registrar'
        elif current_user.is_attendee(event.id):
            data['label'] = 'Attendee'
        else:
            data['label'] = 'User'

    view_kwargs = True
    schema = EventChatMessageSchema
    methods = ['POST', ]
    data_layer = {'session': db.session,
                  'model': EventChatMessage,
                  'methods': {'before_post': before_post}}


class EventChatMessageList(ResourceList):
    """
    List Event Chat Messages
    """

    def query(self, view_kwargs):
        """
        query method for SessionList class
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(EventChatMessage)
        if view_kwargs.get('event_id') is not None:
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            query_ = query_.join(Event).filter(Event.id == event.id).order_by(EventChatMessage.id)

        elif view_kwargs.get('identifier') is not None:
            event = safe_query(db, Event, 'identifier', view_kwargs['identifier'], 'identifier')
            query_ = query_.join(Event).filter(Event.id == event.id).order_by(EventChatMessage.id)
            view_kwargs['id'] = event.id

        elif has_access('is_admin') and view_kwargs.get('event_id') is None and view_kwargs.get('identifier') is None:
            query_ = db.session.query(EventChatMessage)

        return query_

    methods = ['GET']
    schema = EventChatMessageSchema
    data_layer = {'session': db.session,
                  'model': EventChatMessage,
                  'methods': {
                      'query': query
                  }}


class EventChatMessageDetail(ResourceDetail):
    """
    Event Chat Message detail by id
    """

    methods = ['GET', 'DELETE']
    schema = EventChatMessageSchema
    data_layer = {'session': db.session,
                  'model': EventChatMessage}


class EventChatMessageRelationship(ResourceRelationship):
    """
    Event Chat Message Relationship
    """
    schema = EventChatMessageSchema
    methods = ['GET']
    data_layer = {'session': db.session,
                  'model': EventChatMessage}
