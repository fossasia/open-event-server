import factory

from app.models.translation_channels import TranslationChannel
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.video_stream import VideoStreamFactoryBase


class TranslationChannelFactory(BaseFactory):
    class Meta:
        model = TranslationChannel

    video_stream = factory.RelatedFactory(VideoStreamFactoryBase)
    name = common.string_
    url = common.url_
