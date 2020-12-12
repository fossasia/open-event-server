from app.models.video_channel import VideoChannel
from tests.factories import common
from tests.factories.base import BaseFactory


class VideoChannelFactory(BaseFactory):
    class Meta:
        model = VideoChannel

    name = common.string_
    provider = common.string_
    url = common.url_
