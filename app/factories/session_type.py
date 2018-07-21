import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.models.session_type import db, SessionType


class SessionTypeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SessionType
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    length = '00:30'
    event_id = 1
