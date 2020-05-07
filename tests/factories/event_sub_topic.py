import factory

import tests.factories.common as common
from app.models.event_sub_topic import EventSubTopic
from tests.factories.base import BaseFactory
from tests.factories.event_topic import EventTopicFactory


class EventSubTopicFactory(BaseFactory):
    class Meta:
        model = EventSubTopic

    event_topic = factory.RelatedFactory(EventTopicFactory)
    name = common.string_
    slug = common.slug_
    event_topic_id = 1
