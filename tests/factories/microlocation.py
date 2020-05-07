import factory

import tests.factories.common as common
from app.models.microlocation import Microlocation
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


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
