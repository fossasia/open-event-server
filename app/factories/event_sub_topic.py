import factory
from app.models.event_sub_topic import db, EventSubTopic
from app.factories.event_topic import EventTopicFactory
import app.factories.common as common


class EventSubTopicFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = EventSubTopic
        sqlalchemy_session = db.session

    event_topic = factory.RelatedFactory(EventTopicFactory)
    name = common.string_
    slug = common.slug_
    event_topic_id = 1
