import factory

import tests.factories.common as common
from app.models.event_topic import EventTopic, db


class EventTopicFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = EventTopic
        sqlalchemy_session = db.session

    name = common.string_
    slug = common.slug_
    system_image_url = common.imageUrl_
