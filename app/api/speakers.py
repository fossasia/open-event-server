from flask import request
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.bootstrap import api
from app.api.helpers.db import safe_query, get_count, save_to_db
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.permission_manager import has_access
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.speakers import SpeakerSchema
from app.models import db
from app.models.event import Event
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.session_speaker_link import SessionsSpeakersLink
from app.models.user import User


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
        require_relationship(['event', 'user'], data)

        if not has_access('is_coorganizer', event_id=data['event']):
            event = db.session.query(Event).filter_by(id=data['event']).one()
            if event.state == "draft":
                raise ObjectNotFound({'parameter': 'event_id'},
                                     "Event: {} not found".format(data['event_id']))

        if get_count(db.session.query(Event).filter_by(id=int(data['event']), is_sessions_speakers_enabled=False)) > 0:
            raise ForbiddenException({'pointer': ''}, "Speakers are disabled for this Event")

        if get_count(db.session.query(Speaker).filter_by(event_id=int(data['event']), email=data['email'],
                                                         deleted_at=None)) > 0:
            raise ForbiddenException({'pointer': ''}, 'Speaker with this Email ID already exists')

        if 'sessions' in data:
            session_ids = data['sessions']
            for session_id in session_ids:
                if not has_access('is_session_self_submitted', session_id=session_id):
                    raise ObjectNotFound({'parameter': 'session_id'},
                                         "Session: {} not found".format(session_id))

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
    methods = ['POST', ]
    data_layer = {'session': db.session,
                  'model': Speaker,
                  'methods': {
                      'after_create_object': after_create_object
                  }}


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
        query_ = event_query(self, query_, view_kwargs)

        if view_kwargs.get('user_id'):
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            query_ = query_.join(User).filter(User.id == user.id)

        if view_kwargs.get('session_id'):
            session = safe_query(self, Session, 'id', view_kwargs['session_id'], 'session_id')
            # session-speaker :: many-to-many relationship
            query_ = Speaker.query.filter(Speaker.sessions.any(id=session.id))
            if 'Authorization' in request.headers and not has_access('is_coorganizer', event_id=session.event_id):
                if not has_access('is_session_self_submitted', session_id=session.id):
                    query_ = query_.filter(Session.state == "approved" or Session.state == "accepted")

        return query_

    view_kwargs = True
    schema = SpeakerSchema
    methods = ['GET', ]
    data_layer = {'session': db.session,
                  'model': Speaker,
                  'methods': {
                      'query': query,
                  }}


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
                    session_speaker_link = SessionsSpeakersLink(session_state=session.state,
                                                                session_id=session.id,
                                                                event_id=session.event.id,
                                                                speaker_id=speaker.id)
                    save_to_db(session_speaker_link, "Session Speaker Link Saved")

    decorators = (api.has_permission('is_coorganizer_or_user_itself', methods="PATCH,DELETE", fetch="event_id",
                                     fetch_as="event_id", model=Speaker),)
    schema = SpeakerSchema
    data_layer = {'session': db.session,
                  'model': Speaker,
                  'methods': {
                      'before_update_object': before_update_object
                  }}


class SpeakerRelationshipRequired(ResourceRelationship):
    """
    Speaker Relationship class for required entities
    """
    decorators = (api.has_permission('is_coorganizer_or_user_itself', methods="PATCH,DELETE", fetch="event_id",
                                     fetch_as="event_id", model=Speaker),)
    methods = ['GET', 'PATCH']
    schema = SpeakerSchema
    data_layer = {'session': db.session,
                  'model': Speaker}


class SpeakerRelationshipOptional(ResourceRelationship):
    """
    Speaker Relationship class
    """
    decorators = (api.has_permission('is_coorganizer_or_user_itself', methods="PATCH,DELETE", fetch="event_id",
                                     fetch_as="event_id", model=Speaker),)
    schema = SpeakerSchema
    data_layer = {'session': db.session,
                  'model': Speaker}


def start_image_resizing_tasks(speaker, photo_url):
    speaker_id = str(speaker.id)
    from .helpers.tasks import resize_speaker_images_task
    resize_speaker_images_task.delay(speaker_id, photo_url)
