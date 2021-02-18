from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.utilities import require_relationship
from app.api.schema.video_stream_moderators import VideoStreamModeratorSchema
from app.models import db
from app.models.user import User
from app.models.video_stream_moderator import VideoStreamModerator


class VideoStreamModeratorList(ResourceList):
    def before_post(self, args, kwargs, data):
        require_relationship(['video_stream'], data)

    def query(self, view_kwargs):
        query_ = self.session.query(VideoStreamModerator)
        if view_kwargs.get('user_id'):
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            query_ = query_.filter_by(email=user.email)
        elif view_kwargs.get('video_stream_id'):
            query_ = query_.filter_by(video_stream_id=view_kwargs['video_stream_id'])
        return query_

    view_kwargs = True
    decorators = (
        api.has_permission(
            'is_coorganizer', fetch='event_id', model=VideoStreamModerator
        ),
    )
    methods = ['GET', 'POST']
    schema = VideoStreamModeratorSchema
    data_layer = {
        'session': db.session,
        'model': VideoStreamModerator,
        'methods': {'query': query},
    }


class VideoStreamModeratorDetail(ResourceDetail):
    """
    video_stream_moderators detail by id
    """

    view_kwargs = True
    decorators = (
        api.has_permission(
            'is_coorganizer', fetch='event_id', model=VideoStreamModerator
        ),
    )
    methods = ['GET', 'PATCH', 'DELETE']
    schema = VideoStreamModeratorSchema
    data_layer = {
        'session': db.session,
        'model': VideoStreamModerator,
    }


class VideoStreamModeratorRelationship(ResourceRelationship):
    """
    video_stream_moderators Relationship
    """

    methods = ['GET', 'PATCH']
    schema = VideoStreamModeratorSchema
    data_layer = {'session': db.session, 'model': VideoStreamModerator}
