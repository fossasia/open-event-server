from flask_jwt_extended import current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.bootstrap import api
from app.api.helpers.custom_forms import validate_custom_form_constraints_request
from app.api.helpers.db import get_count, safe_query_kwargs, save_to_db
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permission_manager import has_access, is_logged_in
from app.api.helpers.permissions import jwt_required
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.speakers import SpeakerSchema
from app.models import db
from app.models.event import Event
from app.models.session import Session
from app.models.session_speaker_link import SessionsSpeakersLink
from app.models.speaker import Speaker
from app.models.user import User


def check_email_override(data, event_id, speaker=None):
    is_organizer = has_access('is_organizer', event_id=event_id)
    email_overridden = data.get('is_email_overridden')
    if email_overridden and not is_organizer:
        raise ForbiddenError(
            {'pointer': '/data/attributes/is_email_overridden'},
            'Organizer access required to override email',
        )
    if not email_overridden and speaker:
        email_overridden = speaker.is_email_overridden
    if email_overridden:
        data['email'] = None
    elif not data.get('email') or not is_organizer:
        data['email'] = current_user.email


class SpeakerListPost(ResourceList):
    """
    List and create speakers
    """

    def before_post(self, args, kwargs, data=None):
        """
        method to add user_id to view_kwargs before post
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        data['user'] = current_user.id
        require_relationship(['event', 'user'], data)

        if not has_access('is_coorganizer', event_id=data['event']):
            event = db.session.query(Event).filter_by(id=data['event']).one()
            if event.state == "draft":
                raise ObjectNotFound(
                    {'parameter': 'event_id'},
                    "Event: {} not found".format(data['event']),
                )

        if (
            get_count(
                db.session.query(Event).filter_by(
                    id=int(data['event']), is_sessions_speakers_enabled=False
                )
            )
            > 0
        ):
            raise ForbiddenError({'pointer': ''}, "Speakers are disabled for this Event")

        check_email_override(data, data['event'])

        if (
            data.get('email')
            and get_count(
                db.session.query(Speaker).filter_by(
                    event_id=int(data['event']), email=data['email'], deleted_at=None
                )
            )
            > 0
        ):
            raise ForbiddenError(
                {'pointer': ''}, 'Speaker with this Email ID already exists'
            )

        if 'sessions' in data:
            session_ids = data['sessions']
            for session_id in session_ids:
                if not has_access('is_session_self_submitted', session_id=session_id):
                    raise ObjectNotFound(
                        {'parameter': 'session_id'},
                        f"Session: {session_id} not found",
                    )

        excluded = []
        if not data.get('email'):
            # Don't check requirement of email if overriden
            excluded = ['email']
        data['complex_field_values'] = validate_custom_form_constraints_request(
            'speaker', self.schema, Speaker(event_id=data['event']), data, excluded
        )

    def after_create_object(self, speaker, data, view_kwargs):
        """
        after create method to save resized images for speaker
        :param speaker:
        :param data:
        :param view_kwargs:
        :return:
        """

        if data.get('photo_url'):
            start_image_resizing_tasks(speaker, data['photo_url'])

    schema = SpeakerSchema
    decorators = (jwt_required,)
    methods = [
        'POST',
    ]
    data_layer = {
        'session': db.session,
        'model': Speaker,
        'methods': {'after_create_object': after_create_object},
    }


class SpeakerList(ResourceList):
    """
    List speakers based on different params from view_kwargs
    """

    def query(self, view_kwargs):
        """
        query method for speakers list class
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(Speaker)
        query_ = event_query(query_, view_kwargs)

        if view_kwargs.get('user_id'):
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            query_ = query_.join(User).filter(User.id == user.id)

        if view_kwargs.get('session_id'):
            session = safe_query_kwargs(Session, view_kwargs, 'session_id')
            # session-speaker :: many-to-many relationship
            query_ = Speaker.query.filter(Speaker.sessions.any(id=session.id))
            if is_logged_in() and not has_access(
                'is_coorganizer', event_id=session.event_id
            ):
                if not has_access('is_session_self_submitted', session_id=session.id):
                    query_ = query_.filter(
                        Session.state == "approved" or Session.state == "accepted"
                    )

        return query_

    view_kwargs = True
    schema = SpeakerSchema
    methods = [
        'GET',
    ]
    data_layer = {
        'session': db.session,
        'model': Speaker,
        'methods': {
            'query': query,
        },
    }


class SpeakerDetail(ResourceDetail):
    """
    Speakers Detail by id
    """

    def before_update_object(self, speaker, data, view_kwargs):
        """
        method to save image urls before updating speaker object
        :param speaker:
        :param data:
        :param view_kwargs:
        :return:
        """
        if data.get('photo_url') and data['photo_url'] != speaker.photo_url:
            start_image_resizing_tasks(speaker, data['photo_url'])

        check_email_override(data, speaker.event_id, speaker)

        excluded = []
        if not data.get('email'):
            # Don't check requirement of email if overriden
            excluded = ['email']
        data['complex_field_values'] = validate_custom_form_constraints_request(
            'speaker', self.resource.schema, speaker, data, excluded
        )

    def after_patch(self, result):
        """
        method to create session speaker link
        :param result:
        """
        # This method is executed when a new speaker is created
        # and added to an existing session
        speaker_id = result['data']['id']
        speaker = Speaker.query.filter_by(id=speaker_id).first()
        if SessionsSpeakersLink.query.filter_by(speaker_id=speaker_id).count() == 0:
            all_sessions = Session.query.filter_by(deleted_at=None)
            for session in all_sessions:
                if speaker in session.speakers:
                    session_speaker_link = SessionsSpeakersLink(
                        session_id=session.id,
                        event_id=session.event.id,
                        speaker_id=speaker.id,
                    )
                    save_to_db(session_speaker_link, "Session Speaker Link Saved")

    decorators = (
        api.has_permission(
            'is_speaker_itself_or_admin',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=Speaker,
        ),
        api.has_permission(
            'is_coorganizer_or_user_itself',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=Speaker,
        ),
    )
    schema = SpeakerSchema
    data_layer = {
        'session': db.session,
        'model': Speaker,
        'methods': {
            'before_update_object': before_update_object,
        },
    }


class SpeakerRelationshipRequired(ResourceRelationship):
    """
    Speaker Relationship class for required entities
    """

    decorators = (
        api.has_permission(
            'is_coorganizer_or_user_itself',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=Speaker,
        ),
    )
    methods = ['GET', 'PATCH']
    schema = SpeakerSchema
    data_layer = {'session': db.session, 'model': Speaker}


class SpeakerRelationshipOptional(ResourceRelationship):
    """
    Speaker Relationship class
    """

    decorators = (
        api.has_permission(
            'is_coorganizer_or_user_itself',
            methods="PATCH,DELETE",
            fetch="event_id",
            model=Speaker,
        ),
    )
    schema = SpeakerSchema
    data_layer = {'session': db.session, 'model': Speaker}


def start_image_resizing_tasks(speaker, photo_url):
    speaker_id = str(speaker.id)
    from .helpers.tasks import resize_speaker_images_task

    resize_speaker_images_task.delay(speaker_id, photo_url)
