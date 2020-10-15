from flask_rest_jsonapi import ResourceDetail, ResourceList
from flask_rest_jsonapi.resource import ResourceRelationship

from app.api.helpers.db import safe_query_kwargs
from app.api.schema.video_stream import VideoStreamSchema
from app.models import db
from app.models.microlocation import Microlocation
from app.models.video_stream import VideoStream


class VideoStreamList(ResourceList):

    # decorators = (api.has_permission('is_admin', methods="POST"),)

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

    schema = VideoStreamSchema
    # decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    data_layer = {'session': db.session, 'model': VideoStream}


class VideoStreamRelationship(ResourceRelationship):
    """
    User Favourite Events Relationship
    """

    schema = VideoStreamSchema
    methods = ['GET']
    data_layer = {'session': db.session, 'model': VideoStream}
