import factory

from app.models.event_sub_topic import EventSubTopic
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event_topic import EventTopicFactory


class EventSubTopicFactory(BaseFactory):
    class Meta:
        model = EventSubTopic

    event_topic = factory.RelatedFactory(EventTopicFactory)
    name = common.string_
    slug = common.slug_
    event_topic_id = 1
