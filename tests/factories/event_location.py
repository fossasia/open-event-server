import factory

import tests.factories.common as common
from app.models.event_location import EventLocation, db


class EventLocationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = EventLocation
        sqlalchemy_session = db.session

    name = common.string_
    slug = common.slug_
