import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.models.microlocation import db, Microlocation


class MicrolocationFactoryBase(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Microlocation
        sqlalchemy_session = db.session

    name = common.string_
    latitude = common.float_
    longitude = common.float_
    floor = common.int_
    room = common.string_
    event_id = 1


class MicrolocationFactory(MicrolocationFactoryBase):
    event = factory.RelatedFactory(EventFactoryBasic)
