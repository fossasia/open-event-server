from app.models.video_stream import VideoStreamChannel

class VideoStreamChannels(ResourceDetail):
    schema = VideoStreamSchema
    decorators = (jwt_optional,)
    data_layer = {
        'session': db.session,
        'model': VideoStreamChannel,
        'methods': {
            'before_get_object': before_get_object,
            'after_get_object': after_get_object,
            'before_update_object': before_update_object,
            'after_update_object': after_update_object,
            'before_delete_object': before_delete_object,
        },
    }

