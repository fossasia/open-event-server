import tests.factories.common as common
from app.models.event_topic import EventTopic
from tests.factories.base import BaseFactory


class EventTopicFactory(BaseFactory):
    class Meta:
        model = EventTopic

    name = common.string_
    slug = common.slug_
    system_image_url = common.imageUrl_
