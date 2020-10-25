from flask_rest_jsonapi import ResourceDetail, ResourceList
from flask_rest_jsonapi.exceptions import ObjectNotFound
from flask_rest_jsonapi.resource import ResourceRelationship

from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import require_relationship
from app.api.schema.video_stream import VideoStreamSchema
from app.models import db
from app.models.microlocation import Microlocation
from app.models.video_stream import VideoStream


class VideoStreamList(ResourceList):

    # decorators = (api.has_permission('is_admin', methods="POST"),)

    def before_post(self, args, kwargs, data):
        require_relationship(['rooms'], data)
        # if not has_access('is_coorganizer', event_id=data['event']):
        #     raise ObjectNotFound(
        #         {'parameter': 'event_id'}, "Event: {} not found".format(data['event'])
        #     )

    def query(self, view_kwargs):
        query_ = self.session.query(VideoStream)

        if view_kwargs.get('room_id'):
            room = safe_query_kwargs(Microlocation, view_kwargs, 'room_id')
            query_ = query_.join(Microlocation).filter(Microlocation.id == room.id)

        return query_

    schema = VideoStreamSchema
    data_layer = {
        'session': db.session,
        'model': VideoStream,
        'methods': {'query': query},
    }


class VideoStreamDetail(ResourceDetail):
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('room_id'):
            room = safe_query_kwargs(Microlocation, view_kwargs, 'room_id')
            view_kwargs['id'] = room.video_stream and room.video_stream.id

    def after_get_object(self, stream, view_kwargs):
        if not stream.user_can_access:
            raise ObjectNotFound(
                {'parameter': 'id'}, f"Video Stream: {stream.id} not found"
            )

    schema = VideoStreamSchema
    decorators = (jwt_required,)
    # decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
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
