import factory
from app.models.microlocation import db, Microlocation
from app.factories.event import EventFactoryBasic
import app.factories.common as common


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
