from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.bootstrap import api
from app.api.helpers.db import safe_query_by_id
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import require_relationship
from app.api.schema.translation_channels import TranslationChannelSchema
from app.models import db
from app.models.translation_channels import TranslationChannel
from app.models.video_channel import VideoChannel
from app.models.video_stream import VideoStream


class TranslationChannelsList(ResourceList):
    """Get list of Translation Channels"""

    @staticmethod
    def before_get(_args, kwargs):
        """Function called when requesting Translation Channels List"""
        stream_id = kwargs.get("video_stream_id")
        if stream_id:
            vid_stream = safe_query_by_id(VideoStream, stream_id)
            if not vid_stream:

                raise ObjectNotFound(
                    {'parameter': f'{stream_id}'},
                    f"video stream not found for id {stream_id}",
                )

    def query(self, view_kwargs):
        """Query related channels (translations) for specific video stream"""
        if view_kwargs.get("video_stream_id"):
            stream_id = view_kwargs.get("video_stream_id")

            # Do not use all() as it returns a list of object, needs BaseQuery object
            records = self.session.query(TranslationChannel).filter_by(
                video_stream_id=stream_id
            )
            return records
        else:
            return self.session.query(TranslationChannel)

    methods = ["GET"]
    schema = TranslationChannelSchema
    decorators = (jwt_required,)
    data_layer = {
        'session': db.session,
        'model': TranslationChannel,
        'methods': {"query": query, "before_get": before_get},
    }


class TranslationChannelsListPost(ResourceList):
    """Post a list of Translation Channels"""

    @staticmethod
    def before_post(_args, _kwargs, data):
        """Function called when posting to the Translation Channel List"""
        require_relationship(['video_stream', 'channel'], data)
        video_stream = db.session.query(
            VideoStream.query.filter_by(id=data['video_stream']).exists()
        ).scalar()

        channel = db.session.query(
            VideoChannel.query.filter_by(id=data['channel']).exists()
        ).scalar()
        if not video_stream and not channel:
            raise ObjectNotFound(
                {'parameter': 'id'},
                "Incorrect video_stream and channel data in request body",
            )

    schema = TranslationChannelSchema
    decorators = (
        jwt_required,
        api.has_permission('auth_required', methods="POST", model=TranslationChannel),
    )
    methods = ['POST']
    data_layer = {
        'session': db.session,
        'model': TranslationChannel,
        'methods': {"before_post": before_post},
    }


class TranslationChannelsDetail(ResourceDetail):
    """Plain Pattern for the Translation Channel Detail class"""

    schema = TranslationChannelSchema
    decorators = (jwt_required,)
    methods = ['GET', 'PATCH', 'DELETE']
    data_layer = {
        'session': db.session,
        'model': TranslationChannel,
        'methods': {},
    }


class TranslationChannelsRelationship(ResourceRelationship):
    """Plain pattern for the Translation Channel Relationship class"""

    schema = TranslationChannelSchema
    data_layer = {
        'session': db.session,
        'model': TranslationChannel,
        'methods': {},
    }
