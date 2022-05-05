import logging
from uuid import uuid4

from flask import jsonify
from flask.blueprints import Blueprint
from flask_jwt_extended import current_user, jwt_optional
from flask_rest_jsonapi import ResourceDetail, ResourceList
from flask_rest_jsonapi.exceptions import ObjectNotFound
from flask_rest_jsonapi.resource import ResourceRelationship

from app.api.chat.rocket_chat import RocketChatException, get_rocket_chat_token
from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import require_exclusive_relationship
from app.api.schema.video_stream import VideoStreamSchema, ChatmosphereSchema
from app.api.video_channels.bbb import BigBlueButton
from app.models import db
from app.models.event import Event
from app.models.microlocation import Microlocation
from app.models.video_channel import VideoChannel
from app.models.video_recording import VideoRecording
from app.models.video_stream import VideoStream
from app.models.video_stream_moderator import VideoStreamModerator

logger = logging.getLogger(__name__)

streams_routes = Blueprint('streams', __name__, url_prefix='/v1/video-streams')

default_options = {
    'record': True,
    'autoStartRecording': False,
    'muteOnStart': True,
    'endCurrentMeeting': False,
}


def check_same_event(room_ids):
    rooms = Microlocation.query.filter(Microlocation.id.in_(room_ids)).all()
    event_ids = set()
    for room in rooms:
        event_ids.add(room.event_id)
        if len(event_ids) > 1:
            raise ForbiddenError(
                {'pointer': '/data/relationships/rooms'},
                'Video Stream can only be created/edited with rooms of a single event',
            )
    check_event_access(event_ids.pop())


def check_event_access(event_id):
    if not event_id:
        return
    if not has_access('is_coorganizer', event_id=event_id):
        raise ForbiddenError(
            {'pointer': '/data/relationships/rooms'},
            "You don't have access to the provided event",
        )


@streams_routes.route(
    '/<int:stream_id>/join',
)
@jwt_required
def join_stream(stream_id: int):
    stream = VideoStream.query.get_or_404(stream_id)
    if not stream.user_can_access:
        raise NotFoundError({'source': ''}, 'Video Stream Not Found')
    if not stream.channel or stream.channel.provider != 'bbb':
        raise BadRequestError(
            {'param': 'stream_id'},
            'Join action is not applicable on this stream provider',
        )

    options = (
        stream.extra.get('bbb_options')
        or stream.extra.get('jitsi_options')
        or default_options
    )

    params = dict(
        name=stream.name,
        meetingID=stream.extra['response']['meetingID'],
        moderatorPW=stream.extra['response']['moderatorPW'],
        attendeePW=stream.extra['response']['attendeePW'],
        **options,
    )

    channel = stream.channel
    bbb = BigBlueButton(channel.api_url, channel.api_key)
    result = bbb.request('create', params)

    if result.success and result.data:
        stream.extra = {**result.data, 'bbb_options': options}
        db.session.commit()
    elif (
        result.data and result.data.get('response', {}).get('messageKey') == 'idNotUnique'
    ):
        # Meeting is already created
        pass
    else:
        logger.error('Error creating BBB Meeting: %s', result)
        raise BadRequestError('', 'Cannot create Meeting on BigBlueButton')

    join_url = bbb.build_url(
        'join',
        {
            'fullName': current_user.public_name
            or current_user.full_name
            or current_user.anonymous_name,
            'join_via_html5': 'true',
            'meetingID': params['meetingID'],
            'password': params[
                'moderatorPW' if stream.user_is_moderator else 'attendeePW'
            ],
        },
    )

    return jsonify(url=join_url)


def create_bbb_meeting(channel, data):
    # Create BBB meeting
    bbb = BigBlueButton(channel.api_url, channel.api_key)
    meeting_id = str(uuid4())
    options = data['extra'].get('bbb_options') or default_options
    res = bbb.request(
        'create',
        dict(name=data['name'], meetingID=meeting_id, **options),
    )

    if not (res.success and res.data):
        logger.error('Error creating BBB Meeting: %s', res)
        raise UnprocessableEntityError('', 'Cannot create Meeting on BigBlueButton')

    data['extra'] = {**res.data, 'bbb_options': options}


@streams_routes.route(
    '/<int:stream_id>/chat-token',
)
@jwt_required
def get_chat_token(stream_id: int):
    stream = VideoStream.query.get_or_404(stream_id)
    event = stream.event
    if not stream.user_can_access:
        raise NotFoundError({'source': ''}, 'Video Stream Not Found')

    if not event.is_chat_enabled:
        raise NotFoundError({'source': ''}, 'Chat Not Enabled')

    try:
        data = get_rocket_chat_token(current_user, event)
        return jsonify({'success': True, 'token': data['token']})
    except RocketChatException as rce:
        if rce.code == RocketChatException.CODES.DISABLED:
            return jsonify({'success': False, 'code': rce.code})
        else:
            return jsonify(
                {
                    'success': False,
                    'code': rce.code,
                    'response': rce.response is not None and rce.response.json(),
                }
            )


class VideoStreamList(ResourceList):
    def validate(self, data):
        require_exclusive_relationship(['rooms', 'event'], data)
        if data.get('rooms'):
            check_same_event(data['rooms'])
        check_event_access(data.get('event'))
        if data.get('event'):
            video_exists = db.session.query(
                VideoStream.query.filter_by(event_id=data['event']).exists()
            ).scalar()
            if video_exists:
                raise ConflictError(
                    {'pointer': '/data/relationships/event'},
                    'Video Stream for this event already exists',
                )

    def setup_channel(self, data):
        if not data.get('channel'):
            self.channel = None
            return
        channel = VideoChannel.query.get(data['channel'])
        if channel.provider == 'bbb':
            create_bbb_meeting(channel, data)

    def before_post(self, args, kwargs, data):
        self.validate(data)
        self.setup_channel(data)

    def query(self, view_kwargs):
        query_ = self.session.query(VideoStream)

        if view_kwargs.get('room_id'):
            room = safe_query_kwargs(Microlocation, view_kwargs, 'room_id')
            query_ = query_.join(Microlocation).filter(Microlocation.id == room.id)

        return query_

    def after_create_object(self, stream, data, view_kwargs):
        if stream.channel and stream.channel.provider == 'bbb':
            params_isMeetingRunning = dict(
                meetingID=stream.extra['response']['meetingID'],
            )

            channel = stream.channel
            bbb = BigBlueButton(channel.api_url, channel.api_key)
            result_isMeetingRunning = bbb.request(
                'isMeetingRunning', params_isMeetingRunning
            )

            if result_isMeetingRunning.data.get('response', {}).get('running') == 'true':
                params_end_meeting = dict(
                    meetingID=stream.extra['response']['meetingID'],
                    password=stream.extra['response']['moderatorPW'],
                )
                result_end_meeting = bbb.request('end', params_end_meeting)

                if not result_end_meeting.success:
                    logger.error(
                        'Error while ending current BBB Meeting after create BBB meeting: %s',
                        result_end_meeting,
                    )

    schema = VideoStreamSchema
    data_layer = {
        'session': db.session,
        'model': VideoStream,
        'methods': {
            'query': query,
            'after_create_object': after_create_object,
        },
    }


class VideoStreamDetail(ResourceDetail):
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('room_id'):
            room = safe_query_kwargs(Microlocation, view_kwargs, 'room_id')
            view_kwargs['id'] = room.video_stream and room.video_stream.id

        if view_kwargs.get('event_identifier'):
            event = safe_query_kwargs(
                Event, view_kwargs, 'event_identifier', 'identifier'
            )
            view_kwargs['event_id'] = event.id

        if view_kwargs.get('event_id'):
            video_stream = safe_query_kwargs(
                VideoStream, view_kwargs, 'event_id', 'event_id'
            )
            view_kwargs['id'] = video_stream.id

        if view_kwargs.get('video_stream_moderator_id'):
            moderator = safe_query_kwargs(
                VideoStreamModerator, view_kwargs, 'video_stream_moderator_id'
            )
            view_kwargs['id'] = moderator.video_stream_id

        if view_kwargs.get('video_recording_id'):
            video_recording = safe_query_kwargs(
                VideoRecording,
                view_kwargs,
                'video_recording_id',
            )
            view_kwargs['id'] = video_recording.video_stream_id

    def after_get_object(self, stream, view_kwargs):
        if stream and not stream.user_can_access:
            raise ObjectNotFound(
                {'parameter': 'id'}, f"Video Stream: {stream.id} not found"
            )

    @staticmethod
    def check_extra(obj, data):
        if not data.get('extra'):
            return
        channel_id = data.get('channel') or obj.channel_id
        if not channel_id:
            return
        channel = VideoChannel.query.get(channel_id)
        if channel.provider not in ['youtube', 'vimeo', 'bbb', 'jitsi']:
            del data['extra']
        else:
            data['extra'] = {**(obj.extra or {}), **(data.get('extra') or {})}

    @staticmethod
    def setup_channel(obj, data):
        if not data.get('channel') or obj.channel_id == int(data['channel']):
            if not data.get('channel'):
                obj.channel_id = None
            return
        channel = VideoChannel.query.get(data['channel'])
        if channel.provider == 'bbb':
            create_bbb_meeting(channel, data)

    def before_update_object(self, obj, data, kwargs):
        require_exclusive_relationship(['rooms', 'event'], data, optional=True)
        check_event_access(obj.event_id)
        check_event_access(data.get('event'))
        rooms = data.get('rooms', [])
        room_ids = rooms + [room.id for room in obj.rooms]
        if room_ids:
            check_same_event(room_ids)
        VideoStreamDetail.check_extra(obj, data)
        VideoStreamDetail.setup_channel(obj, data)

    def after_update_object(self, stream, data, view_kwargs):
        if stream.channel and stream.channel.provider == 'bbb':
            bbb_options = stream.extra.get('bbb_options')
            if bbb_options and bbb_options.get('endCurrentMeeting'):
                params_isMeetingRunning = dict(
                    meetingID=stream.extra['response']['meetingID'],
                )

                channel = stream.channel
                bbb = BigBlueButton(channel.api_url, channel.api_key)
                result_isMeetingRunning = bbb.request(
                    'isMeetingRunning', params_isMeetingRunning
                )

                if (
                    result_isMeetingRunning.data.get('response', {}).get('running')
                    == 'true'
                ):
                    params_end_meeting = dict(
                        meetingID=stream.extra['response']['meetingID'],
                        password=stream.extra['response']['moderatorPW'],
                    )
                    result_end_meeting = bbb.request('end', params_end_meeting)

                    if not result_end_meeting.success:
                        logger.error(
                            'Error while ending current BBB Meeting: %s',
                            result_end_meeting,
                        )
                        raise BadRequestError(
                            '', 'Cannot end current Meeting on BigBlueButton'
                        )

    def before_delete_object(self, obj, kwargs):
        check_event_access(obj.event_id)
        room_ids = [room.id for room in obj.rooms]
        if room_ids:
            check_same_event(room_ids)

    schema = VideoStreamSchema
    decorators = (jwt_optional,)
    data_layer = {
        'session': db.session,
        'model': VideoStream,
        'methods': {
            'before_get_object': before_get_object,
            'after_get_object': after_get_object,
            'before_update_object': before_update_object,
            'after_update_object': after_update_object,
            'before_delete_object': before_delete_object,
        },
    }


class ChatmosphereDetail(ResourceDetail):
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('event_identifier'):
            event = safe_query_kwargs(
                Event, view_kwargs, 'event_identifier', 'identifier'
            )
            view_kwargs['event_id'] = event.id

        if view_kwargs.get('event_id'):
            video_stream = safe_query_kwargs(
                VideoStream, view_kwargs, 'event_id', 'event_id'
            )
            view_kwargs['id'] = video_stream.id

    def after_get_object(self, stream, view_kwargs):
        if stream and stream.channel.provider != 'chatmosphere':
            raise ObjectNotFound(
                {'parameter': 'id'}, "Chatmosphere stream not created."
            )

    schema = ChatmosphereSchema
    data_layer = {
        'session': db.session,
        'model': VideoStream,
        'methods': {
            'before_get_object': before_get_object,
            'after_get_object': after_get_object,
        },
    }


class VideoStreamRelationship(ResourceRelationship):
    schema = VideoStreamSchema
    methods = ['GET']
    data_layer = {'session': db.session, 'model': VideoStream}
