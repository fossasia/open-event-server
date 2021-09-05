from flask import Blueprint, jsonify
from flask_jwt_extended import current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.db import safe_query_kwargs, save_to_db
from app.api.helpers.errors import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)
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
            if not data['status'] == 'pending':
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
            already_have_session = Session.query.filter(
                Session.id == data['session'],
                Session.speakers.any(Speaker.email == data['email']),
            ).count()
        if already_have_session:
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

        elif view_kwargs.get('event_id'):
            event = safe_query_kwargs(Event, view_kwargs, 'event_id')
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
        if not speaker_invite:
            return
        if not speaker_invite.email == current_user.email:
            if not has_access('is_speaker_for_session', id=speaker_invite.session_id):
                raise ForbiddenError(
                    {'source': ''}, 'Speaker or Invitee access is required.'
                )

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

    methods = ['GET', 'DELETE']
    decorators = (jwt_required,)
    schema = SpeakerInviteSchema
    data_layer = {
        'session': db.session,
        'model': SpeakerInvite,
        'methods': {
            'after_get_object': after_get_object,
            'before_delete_object': before_delete_object,
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


@speaker_invites_misc_routes.route(
    '/speaker-invites/<int:speaker_invite_id>/accept-invite'
)
@jwt_required
def accept_invite(speaker_invite_id):
    try:
        speaker_invite = SpeakerInvite.query.filter_by(id=speaker_invite_id).one()
    except NoResultFound:
        raise NotFoundError({'source': ''}, 'Speaker Invite Not Found')
    else:
        if not current_user.email == speaker_invite.email:
            raise ForbiddenError({'source': ''}, 'Invitee access is required.')
        elif speaker_invite.status == 'accepted':
            raise ConflictError(
                {'pointer': '/data/status'},
                'Speaker invite is already accepted.',
            )
        elif speaker_invite.status == 'rejected':
            raise ConflictError(
                {'pointer': '/data/status'},
                'Rejected speaker invite can not be accepted.',
            )
        try:
            user = User.query.filter_by(email=speaker_invite.email).first()
        except NoResultFound:
            raise NotFoundError(
                {'source': ''}, 'User corresponding to speaker invite not Found'
            )
        if not user.is_verified:
            raise ForbiddenError(
                {'source': ''}, 'User corresponding to speaker invite is unverified.'
            )
        try:
            session = Session.query.filter_by(id=speaker_invite.session_id).one()
        except NoResultFound:
            raise NotFoundError(
                {'source': ''}, 'Session corresponding to speaker invite not Found'
            )
        speaker = Speaker.query.filter_by(
            email=speaker_invite.email, event_id=speaker_invite.event_id
        ).first()
        if not speaker:
            raise NotFoundError(
                {'source': ''}, 'Speaker corresponding to speaker invite not Found'
            )
        try:
            speaker.sessions.append(session)
            db.session.commit()
        except Exception:
            raise UnprocessableEntityError(
                {'source': ''}, 'error while accepting speaker invite.'
            )
        try:
            speaker_invite.status = 'accepted'
            save_to_db(speaker_invite, {'speaker invite accepetd'})
        except Exception:
            raise UnprocessableEntityError(
                {'source': ''}, 'error while accepting speaker invite.'
            )
    return jsonify(
        {
            "email": user.email,
            "event": speaker_invite.event_id,
            "event_identifier": speaker_invite.event.identifier,
            "session": session.id,
            "speaker": speaker.id,
            "name": user.fullname if user.fullname else None,
        }
    )


@speaker_invites_misc_routes.route(
    '/speaker-invites/<int:speaker_invite_id>/reject-invite'
)
@jwt_required
def reject_invite(speaker_invite_id):
    try:
        speaker_invite = SpeakerInvite.query.filter_by(id=speaker_invite_id).one()
    except NoResultFound:
        raise NotFoundError({'source': ''}, 'Speaker Invite Not Found')
    else:
        if not current_user.email == speaker_invite.email:
            raise ForbiddenError({'source': ''}, 'Invitee access is required.')
        elif speaker_invite.status == 'accepted':
            raise ConflictError(
                {'pointer': '/data/status'},
                'Accepted speaker invite can not be rejected.',
            )
        elif speaker_invite.status == 'rejected':
            raise ConflictError(
                {'pointer': '/data/status'},
                'Speaker invite is already rejected.',
            )
        try:
            speaker_invite.status = 'rejected'
            save_to_db(speaker_invite, {'speaker invite rejected'})
        except Exception:
            raise UnprocessableEntityError(
                {'source': ''}, 'error while rejecting speaker invite.'
            )
    return jsonify(
        success=True,
        message="Speaker invite rejected successfully",
    )
