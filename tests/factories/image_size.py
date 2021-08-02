from app.models.image_size import ImageSizes
from tests.factories import common
from tests.factories.base import BaseFactory


class EventImageSizeFactory(BaseFactory):
    class Meta:
        model = ImageSizes

    type = common.string_
    full_width = 10
    full_height = 10
    full_aspect = True
    full_quality = 10
    icon_width = 10
    icon_height = 10
    icon_aspect = True
    icon_quality = 10
    thumbnail_width = 10
    thumbnail_height = 10
    thumbnail_aspect = True
    thumbnail_quality = 10
    logo_width = 10
    logo_height = 10


class SpeakerImageSizeFactory(BaseFactory):
    class Meta:
        model = ImageSizes

    type = common.string_
    icon_size_quality = 80
    small_size_width_height = 50
    thumbnail_size_quality = None
    icon_size_width_height = 35
    thumbnail_size_width_height = 500
    small_size_quality = 80
