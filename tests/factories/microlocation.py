import factory

from app.models.microlocation import Microlocation
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.video_stream import VideoStreamFactoryBase


class MicrolocationFactoryBase(BaseFactory):
    class Meta:
        model = Microlocation

    name = common.string_
    latitude = common.float_
    longitude = common.float_
    floor = common.int_
    room = common.string_
    event_id = 1


class MicrolocationFactory(MicrolocationFactoryBase):
    event = factory.RelatedFactory(EventFactoryBasic)


class MicrolocationSubFactory(MicrolocationFactoryBase):
    event = factory.SubFactory(EventFactoryBasic)


class MicrolocationSubVideoStreamFactory(MicrolocationFactoryBase):
    event = factory.SubFactory(EventFactoryBasic)
    video_stream = factory.SubFactory(VideoStreamFactoryBase)
