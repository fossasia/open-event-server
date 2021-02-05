from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.schema.video_stream_moderators import VideoStreamModeratorSchema
from app.models import db
from app.models.video_stream_moderator import VideoStreamModerator


class VideoStreamModeratorList(ResourceList):
    """
    List and create video_stream_moderators
    """

    def query(self, view_kwargs):
        query_ = self.session.query(VideoStreamModerator)
        if view_kwargs.get('user_id'):
            query_ = query_.filter_by(user_id == view_kwargs['user_id'])
        elif view_kwargs.get('video_stream_id'):
            query_ = query_.filter_by(video_stream_id=view_kwargs['video_stream_id'])
        return query_

    view_kwargs = True
    decorators = (
        api.has_permission(
            'is_coorganizer', fetch='event_id', model=VideoStreamModerator
        ),
    )
    methods = ['GET']
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
