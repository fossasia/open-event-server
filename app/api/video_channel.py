from flask_rest_jsonapi import ResourceDetail, ResourceList

from app.api.bootstrap import api
from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.permission_manager import has_access, is_logged_in
from app.api.schema.video_channel import VideoChannelSchema, VideoChannelSchemaPublic
from app.models import db
from app.models.video_channel import VideoChannel
from app.models.video_stream import VideoStream


class VideoChannelListPost(ResourceList):

    methods = ['POST']
    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = VideoChannelSchema
    data_layer = {
        'session': db.session,
        'model': VideoChannel,
    }


class VideoChannelList(ResourceList):
    def before_get(self, args, kwargs):
        if is_logged_in() and has_access('is_admin'):
            self.schema = VideoChannelSchema
        else:
            self.schema = VideoChannelSchemaPublic

    methods = ['GET']
    schema = VideoChannelSchemaPublic
    data_layer = {
        'session': db.session,
        'model': VideoChannel,
    }


class VideoChannelDetail(ResourceDetail):
    def before_get(self, args, kwargs):
        if is_logged_in() and has_access('is_admin'):
            self.schema = VideoChannelSchema
        else:
            self.schema = VideoChannelSchemaPublic

        if kwargs.get('video_stream_id'):
            stream = safe_query_kwargs(VideoStream, kwargs, 'video_stream_id')
            kwargs['id'] = stream.channel_id

    schema = VideoChannelSchema
    decorators = (
        api.has_permission(
            'is_admin',
            methods="PATCH,DELETE",
        ),
    )
    data_layer = {
        'session': db.session,
        'model': VideoChannel,
    }
