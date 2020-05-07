import tests.factories.common as common
from app.models.event_type import EventType
from tests.factories.base import BaseFactory


class EventTypeFactory(BaseFactory):
    class Meta:
        model = EventType

    name = common.string_
    slug = common.slug_
