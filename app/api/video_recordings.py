from datetime import datetime

from flask_rest_jsonapi import ResourceDetail, ResourceList
from flask_rest_jsonapi.resource import ResourceRelationship

from app.api.helpers.db import get_or_create, safe_query_kwargs
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.schema.video_recordings import VideoRecordingSchema
from app.api.video_channels.bbb import BigBlueButton
from app.models import db
from app.models.video_recording import VideoRecording
from app.models.video_stream import VideoStream


class VideoRecordingList(ResourceList):
    def before_get(self, args, kwargs):
        stream = safe_query_kwargs(VideoStream, kwargs, 'video_stream_id', 'id')
        if not has_access('is_organizer', event_id=stream.event_id):
            raise ForbiddenError(
                {'pointer': 'event_id'},
                'You need to be the event organizer to access video recordings.',
            )

        params = dict(
            meetingID=stream.extra['response']['meetingID'],
        )
        channel = stream.channel
        bbb = BigBlueButton(channel.api_url, channel.api_key)
        result = bbb.request('getRecordings', params)

        if result.data['response']['recordings']:
            recordings = []
            if type(result.data['response']['recordings']['recording']) is list:
                recordings = result.data['response']['recordings']['recording']
            else:
                recordings.append(result.data['response']['recordings']['recording'])
            for recording in recordings:
                get_or_create(
                    VideoRecording,
                    bbb_record_id=recording['recordID'],
                    participants=recording['participants'],
                    url=recording['playback']['format']['url'],
                    start_time=datetime.fromtimestamp(
                        int(int(recording['startTime']) / 1000)
                    ),
                    end_time=datetime.fromtimestamp(
                        int(int(recording['endTime']) / 1000)
                    ),
                    video_stream=stream,
                )

    def query(self, view_kwargs):
        query_ = VideoRecording.query
        if view_kwargs.get('video_stream_id'):
            stream = safe_query_kwargs(VideoStream, view_kwargs, 'video_stream_id')
            query_ = VideoRecording.query.filter(
                VideoRecording.video_stream_id == stream.id
            )
        return query_

    methods = ['GET']
    view_kwargs = True
    decorators = (jwt_required,)
    schema = VideoRecordingSchema
    data_layer = {
        'session': db.session,
        'model': VideoRecording,
        'methods': {
            'query': query,
            'before_get': before_get,
        },
    }


class VideoRecordingDetail(ResourceDetail):
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('video_stream_id'):
            video_stream = safe_query_kwargs(
                VideoStream,
                view_kwargs,
                'video_stream_id',
            )
            view_kwargs['id'] = video_stream.id

    def after_get_object(self, video_recording, view_kwargs):
        if not has_access('is_organizer', event_id=video_recording.video_stream.event_id):
            raise ForbiddenError(
                {'pointer': 'event_id'},
                'You need to be the event organizer to access video recordings.',
            )

    methods = ['GET']
    schema = VideoRecordingSchema
    decorators = (jwt_required,)
    data_layer = {
        'session': db.session,
        'model': VideoRecording,
        'methods': {
            'before_get_object': before_get_object,
            'after_get_object': after_get_object,
        },
    }


class VideoRecordingRelationship(ResourceRelationship):
    schema = VideoRecordingSchema
    methods = ['GET']
    data_layer = {'session': db.session, 'model': VideoRecording}
