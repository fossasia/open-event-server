from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.db import safe_query_kwargs, save_to_db
from app.api.helpers.errors import ConflictError, ForbiddenError, NotFoundError
from app.api.helpers.permission_manager import has_access, jwt_required
from app.api.helpers.utilities import require_relationship
from app.api.schema.speaker_invites import SpeakerInviteSchema
from app.models import db
from app.models.event import Event
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.speaker_invite import SpeakerInvite
from app.models.user import User

speaker_invites_misc_routes = Blueprint(
    'speaker_invites_misc', __name__, url_prefix='/v1'
)


class SpeakerInviteListPost(ResourceList):
    """
    Create speaker invites
    """

    def before_post(self, args, kwargs, data):
        """
        before get method to get the resource id for fetching details
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['session', 'event'], data)
        if not has_access('is_speaker_for_session', id=data['session']):
            raise ForbiddenError({'source': ''}, 'Speaker access is required.')
        if data.get('status'):
            if data['status'] == 'accepted':
                raise ForbiddenError(
                    {'source': ''}, 'Speaker Invite can not created with accepted status.'
                )

    def before_create_object(self, data, view_kwargs):
        """
        before create object method for SpeakerInviteListPost Class
        :param data:
        :param view_kwargs:
        :return:
        """
        if 'email' in data and 'session' in data:
            invite_already_exists = SpeakerInvite.query.filter_by(
                email=data['email'], session_id=data['session'], status='pending'
            ).count()
            already_speaker = Session.query.filter(
                Session.id == data['session'],
                Session.speakers.any(Speaker.email == data['email']),
            ).count()
        if already_speaker:
            raise ForbiddenError({'source': '/data'}, 'Invitee is already a speaker.')
        if invite_already_exists:
            raise ConflictError(
                {'source': '/data'},
                'Speaker Invite has already been sent for this email.',
            )

    def after_create_object(self, speaker_invite, data, view_kwargs):
        """
        after create object method for role invite links
        :param role_invite:
        :param data:
        :param view_kwargs:
        :return:
        """
        speaker_invite.send_invite(inviter_email=current_user.email)

    view_kwargs = True
    methods = ['POST']
    decorators = (jwt_required,)
    schema = SpeakerInviteSchema
    data_layer = {
        'session': db.session,
        'model': SpeakerInvite,
        'methods': {
            'before_create_object': before_create_object,
            'after_create_object': after_create_object,
        },
    }


class SpeakerInviteList(ResourceList):
    """
    List speaker invites based on session_id
    """

    def query(self, view_kwargs):
        query_ = SpeakerInvite.query
        if view_kwargs.get('session_id'):
            session = safe_query_kwargs(Session, view_kwargs, 'session_id')
            if not has_access('is_speaker_for_session', id=session.id):
                raise ForbiddenError({'source': ''}, 'Speaker access is required.')
            query_ = query_.filter_by(session_id=session.id)

        elif view_kwargs.get('speaker_id'):
            speaker = safe_query_kwargs(Speaker, view_kwargs, 'speaker_id')
            if not speaker.email == current_user.email:
                raise ForbiddenError({'source': ''}, 'Invitee access is required.')
            query_ = query_.filter_by(speaker_id=speaker.id)

        elif view_kwargs.get('event_id'):
            event = safe_query_kwargs(Event, view_kwargs, 'event_id')
            if not has_access('is_coorganizer', event_id=event.id):
                raise ForbiddenError({'source': ''}, "Minimum Organizer access required")
            query_ = query_.filter_by(event_id=event.id)

        elif not has_access('is_admin'):
            raise ForbiddenError({'pointer': 'user_id'}, 'Admin Access Required')

        return query_

    view_kwargs = True
    methods = ['GET']
    decorators = (jwt_required,)
    schema = SpeakerInviteSchema
    data_layer = {
        'session': db.session,
        'model': SpeakerInvite,
        'methods': {'query': query},
    }


class SpeakerInviteDetail(ResourceDetail):
    """
    Speaker invite detail by id
    """

    def after_get_object(self, speaker_invite, view_kwargs):
        """
        after get method for Speaker Invite detail
        :param view_kwargs:
        :return:
        """
        if not speaker_invite.email == current_user.email:
            if not has_access('is_speaker_for_session', id=speaker_invite.session_id):
                raise ForbiddenError(
                    {'source': ''}, 'Speaker or Invitee access is required.'
                )

    def before_update_object(self, speaker_invite, data, view_kwargs):
        """
        method to check for proper permissions for updating
        :param custom_placeholder:
        :param data:
        :param view_kwargs:
        :return:
        """
        if speaker_invite.status == 'accepted':
            raise ConflictError(
                {'pointer': '/data/status'},
                'You cannot update an accepted speaker invite.',
            )
        if not speaker_invite.email == current_user.email:
            raise ForbiddenError({'source': ''}, 'Invitee access is required.')
        if (
            data['email'] != speaker_invite.email
            or int(data['session']) != speaker_invite.session_id
            or int(data['event']) != speaker_invite.event_id
        ):
            raise ForbiddenError(
                {'source': ''},
                'Invitee can only update status and speaker of speaker invite.',
            )
        elif data.get('speaker'):
            speaker = Speaker.query.get_or_404(data['speaker'])
            if speaker.email != current_user.email:
                raise ForbiddenError(
                    {'source': ''}, 'Invitee can only add himself as speaker.'
                )
        elif data.get('status'):
            if data['status'] == 'pending' and data['status'] != speaker_invite.status:
                raise ForbiddenError(
                    {'source': ''}, 'Invitee can not change status to pending.'
                )

    def after_update_object(self, speaker_invite, data, view_kwargs):
        if speaker_invite.status == 'accepted':
            user = User.query.filter(User.id == speaker_invite.speaker.user_id).first()
            if not user.is_verified:
                user.is_verified = True
                save_to_db(user, 'user is verified')

    def before_delete_object(self, speaker_invite, view_kwargs):
        """
        method to check for proper permissions for deleting
        :param order:
        :param view_kwargs:
        :return:
        """
        if not has_access('is_speaker_for_session', id=speaker_invite.session_id):
            raise ForbiddenError({'source': ''}, 'Speaker access is required.')
        if speaker_invite.status == 'accepted':
            raise ConflictError(
                {'pointer': '/data/status'},
                'You cannot delete an accepted speaker invite.',
            )

    methods = ['GET', 'PATCH', 'DELETE']
    decorators = (jwt_required,)
    schema = SpeakerInviteSchema
    data_layer = {
        'session': db.session,
        'model': SpeakerInvite,
        'methods': {
            'before_delete_object': before_delete_object,
            'after_get_object': after_get_object,
            'before_update_object': before_update_object,
            'after_update_object': after_update_object,
        },
    }


class SpeakerInviteRelationship(ResourceRelationship):
    """
    Speaker invite Relationship
    """

    decorators = (jwt_required,)
    methods = ['GET']
    schema = SpeakerInviteSchema
    data_layer = {'session': db.session, 'model': SpeakerInvite}


@speaker_invites_misc_routes.route('/speaker_invites/user', methods=['POST'])
def fetch_user():
    token = request.json['data']['token']
    try:
        speaker_invite = SpeakerInvite.query.filter_by(token=token).one()
    except NoResultFound:
        raise NotFoundError({'source': ''}, 'Speaker Invite Not Found')
    else:
        if speaker_invite.status != 'pending':
            NotFoundError({'source': ''}, 'Speaker Invite Not Found')
        user = User.query.filter(User.email == speaker_invite.email).first()
        is_registered = True if user else False
        return jsonify(
            {
                "email": speaker_invite.email,
                "invite_status": speaker_invite.status,
                "is_registered": is_registered,
            }
        )


@speaker_invites_misc_routes.route('/speaker_invites/speaker', methods=['POST'])
@jwt_required
def fetch_speaker():
    token = request.json['data']['token']
    try:
        speaker_invite = SpeakerInvite.query.filter_by(token=token).one()
    except NoResultFound:
        raise NotFoundError({'source': ''}, 'Speaker Invite Not Found')
    else:
        if current_user.email == speaker_invite.email:
            if speaker_invite.speaker:
                return jsonify({"is_already_created": True})
            speaker = Speaker.query.filter_by(
                email=speaker_invite.email, event_id=speaker_invite.event_id
            ).first()
            if speaker:
                speaker_invite.speaker_id = speaker.id
                save_to_db(speaker_invite, 'Add speaker in speaker_invite')
                return jsonify({"is_already_created": True})
            else:
                return jsonify({"is_already_created": False})
        else:
            raise ForbiddenError({'source': ''}, 'Invitee access is required.')


@speaker_invites_misc_routes.route('/speaker_invites/data', methods=['POST'])
@jwt_required
def fetch_data():
    token = request.json['data']['token']
    try:
        speaker_invite = SpeakerInvite.query.filter_by(token=token).one()
    except NoResultFound:
        raise NotFoundError({'source': ''}, 'Speaker Invite Not Found')
    else:
        if current_user.email == speaker_invite.email:
            return jsonify(
                {
                    "email": speaker_invite.email,
                    "status": speaker_invite.status,
                    "invite_id": speaker_invite.id,
                    "event_id": speaker_invite.event_id,
                    "session_id": speaker_invite.session_id,
                    "speaker_id": speaker_invite.speaker_id,
                }
            )
        else:
            raise ForbiddenError({'source': ''}, 'Invitee access is required.')
