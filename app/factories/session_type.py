import factory
from app.models.session_type import db, SessionType
from app.factories.event import EventFactoryBasic
import app.factories.common as common


class SessionTypeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SessionType
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    length = '00:30'
    event_id = 1
