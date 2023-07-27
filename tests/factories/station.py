import factory

from app.models.station import Station
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.microlocation import MicrolocationFactory


class StationFactoryBase(BaseFactory):
    class Meta:
        model = Station

    station_name = common.string_
    station_type = common.string_


class StationFactory(StationFactoryBase):
    event = factory.RelatedFactory(EventFactoryBasic)
    microlocation = factory.RelatedFactory(MicrolocationFactory)


class StationSubFactory(StationFactoryBase):
    event = factory.SubFactory(EventFactoryBasic)
    microlocation = factory.SubFactory(MicrolocationFactory)
