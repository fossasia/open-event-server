from flask_jwt_extended import current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.mail import send_email_to_moderator
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import require_relationship
from app.api.schema.video_stream_moderators import VideoStreamModeratorSchema
from app.models import db
from app.models.user import User
from app.models.video_stream import VideoStream
from app.models.video_stream_moderator import VideoStreamModerator


class VideoStreamModeratorList(ResourceList):
    def before_post(self, args, kwargs, data):
        require_relationship(['video_stream'], data)
        stream = safe_query_kwargs(VideoStream, data, 'video_stream')
        if not has_access('is_coorganizer', event_id=stream.event_id):
            raise ForbiddenError({'pointer': 'user_id'}, 'Co-Organizer access required')

    def after_create_object(self, video_stream_moderator, data, view_kwargs):
        send_email_to_moderator(video_stream_moderator)

    def query(self, view_kwargs):
        query_ = self.session.query(VideoStreamModerator)
        if user_id := view_kwargs.get('user_id'):
            if current_user.id != int(user_id):
                raise ForbiddenError(
                    {'pointer': 'user_id'}, "Cannot access other user's data"
                )
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            query_ = query_.filter_by(email=user.email)
        elif view_kwargs.get('video_stream_id'):
            stream = safe_query_kwargs(VideoStream, view_kwargs, 'video_stream_id')
            if not has_access('is_coorganizer', event_id=stream.event_id):
                raise ForbiddenError(
                    {'pointer': 'user_id'}, 'Co-Organizer access required'
                )
            query_ = query_.filter_by(video_stream_id=view_kwargs['video_stream_id'])
        else:
            raise ForbiddenError({'pointer': 'query'}, 'Cannot query all moderators')
        return query_

    view_kwargs = True
    decorators = (jwt_required,)
    methods = ['GET', 'POST']
    schema = VideoStreamModeratorSchema
    data_layer = {
        'session': db.session,
        'model': VideoStreamModerator,
        'methods': {'query': query, 'after_create_object': after_create_object},
    }


class VideoStreamModeratorDetail(ResourceDetail):
    """
    video_stream_moderators detail by id
    """

    def after_get_object(self, obj, kwargs):
        if not has_access('is_coorganizer', event_id=obj.video_stream.event_id):
            raise ForbiddenError({'pointer': 'user_id'}, 'Co-Organizer access required')

    view_kwargs = True
    decorators = (jwt_required,)
    methods = ['GET', 'PATCH', 'DELETE']
    schema = VideoStreamModeratorSchema
    data_layer = {
        'session': db.session,
        'model': VideoStreamModerator,
        'methods': {'after_get_object': after_get_object},
    }


class VideoStreamModeratorRelationship(ResourceRelationship):
    """
    video_stream_moderators Relationship
    """

    methods = ['GET', 'PATCH']
    schema = VideoStreamModeratorSchema
    data_layer = {'session': db.session, 'model': VideoStreamModerator}
