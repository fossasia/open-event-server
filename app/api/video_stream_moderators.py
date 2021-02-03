from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.query import event_query
from app.api.schema.video_stream_moderators import VideoStreamModeratorSchema
from app.models import db
from app.models.video_stream_moderator import VideoStreamModerator


class VideoStreamModeratorList(ResourceList):
    """
    List and create video_stream_moderators
    """

    def query(self, view_kwargs):
        query_ = self.session.query(VideoStreamModerator)
        query_ = event_query(query_, view_kwargs)

        return query_

    view_kwargs = True
    decorators = (
        api.has_permission(
            'is_coorganizer', fetch='video_stream_id', model=VideoStreamModerator
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

    methods = ['GET', 'PATCH', 'DELETE']
    decorators = (
        api.has_permission(
            'is_coorganizer', fetch='video_stream_id', model=VideoStreamModerator
        ),
    )
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
