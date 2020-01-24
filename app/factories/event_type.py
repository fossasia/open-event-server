import factory

import app.factories.common as common
from app.models.event_type import EventType, db


class EventTypeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = EventType
        sqlalchemy_session = db.session

    name = common.string_
    slug = common.slug_
