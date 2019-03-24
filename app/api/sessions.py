from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.events import Event
from app.api.helpers.db import safe_query, get_count, save_to_db
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.mail import send_email_new_session, send_email_session_accept_reject
from app.api.helpers.notification import send_notif_new_session_organizer, send_notif_session_accept_reject
from app.api.helpers.permissions import current_identity
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.sessions import SessionSchema
from app.models import db
from app.models.microlocation import Microlocation
from app.models.session import Session
from app.models.session_type import SessionType
from app.models.speaker import Speaker
from app.models.track import Track
from app.models.user import User
from app.models.session_speaker_link import SessionsSpeakersLink
from app.settings import get_settings


class SessionListPost(ResourceList):
    """
    List Sessions
    """
    def before_post(self, args, kwargs, data):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event', 'track'], data)
        data['creator_id'] = current_identity.id
        if get_count(db.session.query(Event).filter_by(id=int(data['event']), is_sessions_speakers_enabled=False)) > 0:
            raise ForbiddenException({'pointer': ''}, "Sessions are disabled for this Event")

    def after_create_object(self, session, data, view_kwargs):
        """
        method to send email for creation of new session
        mails session link to the concerned user
        :param session:
        :param data:
        :param view_kwargs:
        :return:
        """
        if session.event.get_organizer():
            event_name = session.event.name
            organizer = session.event.get_organizer()
            organizer_email = organizer.email
            frontend_url = get_settings()['frontend_url']
            event = session.event
            link = "{}/events/{}/sessions/{}"\
                .format(frontend_url, event.identifier, session.id)
            send_email_new_session(organizer_email, event_name, link)
            send_notif_new_session_organizer(organizer, event_name, link, session.id)

        for speaker in session.speakers:
            session_speaker_link = SessionsSpeakersLink(session_state=session.state,
                                                        session_id=session.id,
                                                        event_id=session.event.id,
                                                        speaker_id=speaker.id)
            save_to_db(session_speaker_link, "Session Speaker Link Saved")

    decorators = (api.has_permission('create_event'),)
    schema = SessionSchema
    data_layer = {'session': db.session,
                  'model': Session,
                  'methods': {'after_create_object': after_create_object
                              }}


class SessionList(ResourceList):
    """
    List Sessions
    """

    def query(self, view_kwargs):
        """
        query method for SessionList class
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(Session)
        if view_kwargs.get('track_id') is not None:
            track = safe_query(self, Track, 'id', view_kwargs['track_id'], 'track_id')
            query_ = query_.join(Track).filter(Track.id == track.id)
        if view_kwargs.get('session_type_id') is not None:
            session_type = safe_query(self, SessionType, 'id', view_kwargs['session_type_id'], 'session_type_id')
            query_ = query_.join(SessionType).filter(SessionType.id == session_type.id)
        if view_kwargs.get('microlocation_id') is not None:
            microlocation = safe_query(self, Microlocation, 'id', view_kwargs['microlocation_id'], 'microlocation_id')
            query_ = query_.join(Microlocation).filter(Microlocation.id == microlocation.id)
        if view_kwargs.get('user_id') is not None:
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            query_ = query_.join(User)\
                .join(Speaker).filter((User.id == user.id or Session.speakers.any(Speaker.user_id == user.id)))
        query_ = event_query(self, query_, view_kwargs)
        if view_kwargs.get('speaker_id'):
            speaker = safe_query(self, Speaker, 'id', view_kwargs['speaker_id'], 'speaker_id')
            # session-speaker :: many-to-many relationship
            query_ = Session.query.filter(Session.speakers.any(id=speaker.id))

        return query_

    view_kwargs = True
    methods = ['GET']
    schema = SessionSchema
    data_layer = {'session': db.session,
                  'model': Session,
                  'methods': {
                      'query': query
                  }}


class SessionDetail(ResourceDetail):
    """
    Session detail by id
    """
    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'identifier')
            view_kwargs['event_id'] = event.id

    def after_update_object(self, session, data, view_kwargs):
        """ Send email if session accepted or rejected """

        if 'state' in data and data.get('send_email', None) and (session.state == 'accepted' or
                                                                 session.state == 'rejected'):

            event = session.event
            # Email for speaker
            speakers = session.speakers
            for speaker in speakers:
                frontend_url = get_settings()['frontend_url']
                link = "{}/events/{}/sessions/{}" \
                    .format(frontend_url, event.identifier, session.id)
                send_email_session_accept_reject(speaker.email, session, link)
                send_notif_session_accept_reject(speaker, session.title, session.state, link, session.id)

            # Email for organizer
            if session.event.get_organizer():
                organizer = session.event.get_organizer()
                organizer_email = organizer.email
                frontend_url = get_settings()['frontend_url']
                link = "{}/events/{}/sessions/{}" \
                    .format(frontend_url, event.identifier, session.id)
                send_email_session_accept_reject(organizer_email, session,
                                                 link)
                send_notif_session_accept_reject(organizer, session.title,
                                                 session.state, link, session.id)
        if 'state' in data:
            entry_count = SessionsSpeakersLink.query.filter_by(session_id=session.id)
            if entry_count.count() == 0:
                is_patch_request = False
            else:
                is_patch_request = True

            if is_patch_request:
                for focus_session in entry_count:
                    focus_session.session_state = session.state
                db.session.commit()
            else:
                current_session = Session.query.filter_by(id=session.id).first()
                for speaker in current_session.speakers:
                    session_speaker_link = SessionsSpeakersLink(session_state=session.state,
                                                                session_id=session.id,
                                                                event_id=session.event.id,
                                                                speaker_id=speaker.id)
            save_to_db(session_speaker_link, "Session Speaker Link Saved")

    decorators = (api.has_permission('is_speaker_for_session', methods="PATCH,DELETE"),)
    schema = SessionSchema
    data_layer = {'session': db.session,
                  'model': Session,
                  'methods': {'before_get_object': before_get_object,
                              'after_update_object': after_update_object}}


class SessionRelationshipRequired(ResourceRelationship):
    """
    Session Relationship
    """
    schema = SessionSchema
    decorators = (api.has_permission('is_speaker_for_session', methods="PATCH,DELETE"),)
    methods = ['GET', 'PATCH']
    data_layer = {'session': db.session,
                  'model': Session}


class SessionRelationshipOptional(ResourceRelationship):
    """
    Session Relationship
    """
    schema = SessionSchema
    decorators = (api.has_permission('is_speaker_for_session', methods="PATCH,DELETE"),)
    data_layer = {'session': db.session,
                  'model': Session}
