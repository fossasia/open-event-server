import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.models.microlocation import db, Microlocation


class MicrolocationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Microlocation
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    latitude = common.float_
    longitude = common.float_
    floor = common.int_
    room = common.string_
    event_id = 1
