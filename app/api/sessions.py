from flask_jwt_extended import current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.events import Event
from app.api.helpers.db import get_count, safe_query, safe_query_kwargs, save_to_db
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.files import make_frontend_url
from app.api.helpers.mail import send_email_new_session, send_email_session_accept_reject
from app.api.helpers.notification import (
    send_notif_new_session_organizer,
    send_notif_session_accept_reject,
)
from app.api.helpers.permission_manager import has_access
from app.api.helpers.query import event_query
from app.api.helpers.speaker import can_edit_after_cfs_ends
from app.api.helpers.utilities import require_relationship
from app.api.schema.sessions import SessionSchema
from app.models import db
from app.models.microlocation import Microlocation
from app.models.session import Session
from app.models.session_speaker_link import SessionsSpeakersLink
from app.models.session_type import SessionType
from app.models.speaker import Speaker
from app.models.track import Track
from app.models.user import User
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
        data['creator_id'] = current_user.id
        if (
            get_count(
                db.session.query(Event).filter_by(
                    id=int(data['event']), is_sessions_speakers_enabled=False
                )
            )
            > 0
        ):
            raise ForbiddenError({'pointer': ''}, "Sessions are disabled for this Event")

    def after_create_object(self, session, data, view_kwargs):
        """
        method to send email for creation of new session
        mails session link to the concerned user
        :param session:
        :param data:
        :param view_kwargs:
        :return:
        """
        if session.event.get_owner():
            event_name = session.event.name
            owner = session.event.get_owner()
            owner_email = owner.email
            event = session.event
            link = make_frontend_url(
                "/events/{}/sessions/{}".format(event.identifier, session.id)
            )
            send_email_new_session(owner_email, event_name, link)
            send_notif_new_session_organizer(owner, event_name, link, session.id)

        for speaker in session.speakers:
            session_speaker_link = SessionsSpeakersLink(
                session_state=session.state,
                session_id=session.id,
                event_id=session.event.id,
                speaker_id=speaker.id,
            )
            save_to_db(session_speaker_link, "Session Speaker Link Saved")

    decorators = (api.has_permission('create_event'),)
    schema = SessionSchema
    data_layer = {
        'session': db.session,
        'model': Session,
        'methods': {'after_create_object': after_create_object},
    }


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
            track = safe_query_kwargs(Track, view_kwargs, 'track_id')
            query_ = query_.join(Track).filter(Track.id == track.id)
        if view_kwargs.get('session_type_id') is not None:
            session_type = safe_query_kwargs(SessionType, view_kwargs, 'session_type_id')
            query_ = query_.join(SessionType).filter(SessionType.id == session_type.id)
        if view_kwargs.get('microlocation_id') is not None:
            microlocation = safe_query_kwargs(
                Microlocation, view_kwargs, 'microlocation_id',
            )
            query_ = query_.join(Microlocation).filter(
                Microlocation.id == microlocation.id
            )
        if view_kwargs.get('user_id') is not None:
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            query_ = (
                query_.join(User)
                .join(Speaker)
                .filter(
                    (
                        User.id == user.id
                        or Session.speakers.any(Speaker.user_id == user.id)
                    )
                )
            )
        query_ = event_query(query_, view_kwargs)
        if view_kwargs.get('speaker_id'):
            speaker = safe_query_kwargs(Speaker, view_kwargs, 'speaker_id')
            # session-speaker :: many-to-many relationship
            query_ = Session.query.filter(Session.speakers.any(id=speaker.id))

        return query_

    view_kwargs = True
    methods = ['GET']
    schema = SessionSchema
    data_layer = {'session': db.session, 'model': Session, 'methods': {'query': query}}


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
            event = safe_query(
                Event, 'identifier', view_kwargs['event_identifier'], 'identifier'
            )
            view_kwargs['event_id'] = event.id

    def before_update_object(self, session, data, view_kwargs):
        """
        before update method to verify if session is locked before updating session object
        :param event:
        :param data:
        :param view_kwargs:
        :return:
        """
        if data.get('is_locked') != session.is_locked:
            if not (
                has_access('is_admin')
                or has_access('is_organizer', event_id=session.event_id)
            ):
                raise ForbiddenError(
                    {'source': '/data/attributes/is-locked'},
                    "You don't have enough permissions to change this property",
                )

        if session.is_locked and data.get('is_locked') == session.is_locked:
            raise ForbiddenError(
                {'source': '/data/attributes/is-locked'},
                "Locked sessions cannot be edited",
            )

        if not can_edit_after_cfs_ends(session.event_id):
            raise ForbiddenError(
                {'source': ''}, "Cannot edit session after the call for speaker is ended"
            )

    def after_update_object(self, session, data, view_kwargs):
        """ Send email if session accepted or rejected """

        if (
            'state' in data
            and data.get('send_email', None)
            and (session.state == 'accepted' or session.state == 'rejected')
        ):

            event = session.event
            # Email for speaker
            speakers = session.speakers
            for speaker in speakers:
                frontend_url = get_settings()['frontend_url']
                link = "{}/events/{}/sessions/{}".format(
                    frontend_url, event.identifier, session.id
                )
                if not speaker.is_email_overridden:
                    send_email_session_accept_reject(speaker.email, session, link)
                    send_notif_session_accept_reject(
                        speaker, session.title, session.state, link, session.id
                    )

            # Email for owner
            if session.event.get_owner():
                owner = session.event.get_owner()
                owner_email = owner.email
                frontend_url = get_settings()['frontend_url']
                link = "{}/events/{}/sessions/{}".format(
                    frontend_url, event.identifier, session.id
                )
                send_email_session_accept_reject(owner_email, session, link)
                send_notif_session_accept_reject(
                    owner, session.title, session.state, link, session.id
                )
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
                    session_speaker_link = SessionsSpeakersLink(
                        session_state=session.state,
                        session_id=session.id,
                        event_id=session.event.id,
                        speaker_id=speaker.id,
                    )
                    save_to_db(session_speaker_link, "Session Speaker Link Saved")

    decorators = (api.has_permission('is_speaker_for_session', methods="PATCH,DELETE"),)
    schema = SessionSchema
    data_layer = {
        'session': db.session,
        'model': Session,
        'methods': {
            'before_update_object': before_update_object,
            'before_get_object': before_get_object,
            'after_update_object': after_update_object,
        },
    }


class SessionRelationshipRequired(ResourceRelationship):
    """
    Session Relationship
    """

    schema = SessionSchema
    decorators = (api.has_permission('is_speaker_for_session', methods="PATCH,DELETE"),)
    methods = ['GET', 'PATCH']
    data_layer = {'session': db.session, 'model': Session}


class SessionRelationshipOptional(ResourceRelationship):
    """
    Session Relationship
    """

    schema = SessionSchema
    decorators = (api.has_permission('is_speaker_for_session', methods="PATCH,DELETE"),)
    data_layer = {'session': db.session, 'model': Session}
