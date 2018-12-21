import factory

import app.factories.common as common
from app.models.event_location import db, EventLocation


class EventLocationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = EventLocation
        sqlalchemy_session = db.session

    name = common.string_
    slug = common.slug_
