from app.models.video_stream import VideoStream
from tests.factories import common
from tests.factories.base import BaseFactory


class VideoStreamFactoryBase(BaseFactory):
    class Meta:
        model = VideoStream

    name = common.string_
    url = common.url_
    password = common.string_
    additional_information = common.string_
