from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask import request, current_app as app
from flask_jwt import current_identity as current_user, _jwt_required

from app.models.session import Session
from app.api.helpers.db import safe_query
from app.api.helpers.permission_manager import has_access
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.utilities import require_relationship
from app.api.schema.session_chat_messages import SessionChatMessageSchema
from app.models import db
from app.models.session_chat_message import SessionChatMessage
from app.models.speaker import Speaker
from app.models.ticket_holder import TicketHolder


class SessionChatMessageListPost(ResourceList):
    """
    Create Session Chat Messages
    """
    @classmethod
    def before_post(self, args, kwargs, data):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """

        if 'Authorization' in request.headers:
            _jwt_required(app.config['JWT_DEFAULT_REALM'])
        else:
            raise ForbiddenException({'source': ''}, 'Authorization required')
        require_relationship(['session'], data)

        data['user'] = current_user.id
        session = db.session.query(Session).filter_by(id=int(data['session'])).first()
        event_id = session.event_id
        attendee = db.session.query(TicketHolder).filter_by(event_id=event_id, email=current_user.email).first()
        speaker = db.session.query(Speaker).filter_by(event_id=event_id, user_id=current_user.id).first()
        if speaker:
            data['label'] = 'Speaker'
        elif attendee:
            data['label'] = 'Attendee'
        else:
            raise ForbiddenException({'source': ''}, 'Only Authorized Speakers or Attendees' +
                                     'can chat in Session Chat Room')

    view_kwargs = True
    schema = SessionChatMessageSchema
    methods = ['POST', ]
    data_layer = {'session': db.session,
                  'model': SessionChatMessage,
                  'methods': {'before_post': before_post}}


class SessionChatMessageList(ResourceList):
    """
    List Session Chat Messages
    """
    def query(self, view_kwargs):
        """
        query method for SessionChatMessageList class
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(SessionChatMessage)
        if view_kwargs.get('session_id') is not None:
            session = safe_query(self, Session, 'id', view_kwargs['session_id'], 'sesssion_id')
            query_ = query_.join(Session).filter(Session.id == session.id).order_by(SessionChatMessage.id)
        elif has_access('is_admin') and view_kwargs.get('session_id') is None:
            pass
        return query_

    methods = ['GET']
    schema = SessionChatMessageSchema
    data_layer = {'session': db.session,
                  'model': SessionChatMessage,
                  'methods': {
                      'query': query
                  }}


class SessionChatMessageDetail(ResourceDetail):
    """
    Session Chat Message detail by id
    """

    methods = ['GET', 'DELETE']
    schema = SessionChatMessageSchema
    data_layer = {'session': db.session,
                  'model': SessionChatMessage}


class SessionChatMessageRelationship(ResourceRelationship):
    """
    Session Chat Message Relationship
    """
    schema = SessionChatMessageSchema
    methods = ['GET']
    data_layer = {'session': db.session,
                  'model': SessionChatMessage}
