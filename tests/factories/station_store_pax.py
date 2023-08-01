import factory

from app.models.station_store_pax import StationStorePax
from tests.factories.base import BaseFactory
from tests.factories.session import SessionFactory
from tests.factories.station import StationFactory


class StationStorePaxFactory(BaseFactory):
    class Meta:
        model = StationStorePax

    current_pax = 10
    station = factory.RelatedFactory(StationFactory)
    session = factory.RelatedFactory(SessionFactory)
