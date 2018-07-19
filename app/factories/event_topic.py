import factory

import app.factories.common as common
from app.models.event_topic import db, EventTopic


class EventTopicFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = EventTopic
        sqlalchemy_session = db.session

    name = common.string_
    slug = common.slug_
