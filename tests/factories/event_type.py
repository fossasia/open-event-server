from app.models.event_type import EventType
from tests.factories import common as common
from tests.factories.base import BaseFactory


class EventTypeFactory(BaseFactory):
    class Meta:
        model = EventType

    name = common.string_
    slug = common.slug_
