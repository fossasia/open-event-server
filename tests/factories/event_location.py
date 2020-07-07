from app.models.event_location import EventLocation
from tests.factories import common
from tests.factories.base import BaseFactory


class EventLocationFactory(BaseFactory):
    class Meta:
        model = EventLocation

    name = common.string_
    slug = common.slug_
