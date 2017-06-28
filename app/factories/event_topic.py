import factory
from app.models.event_topic import db, EventTopic
import app.factories.common as common


class EventTopicFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = EventTopic
        sqlalchemy_session = db.session

    name = common.string_
    slug = common.slug_
