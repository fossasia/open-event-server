import factory

import tests.factories.common as common
from tests.factories.event import EventFactoryBasic
from app.models.session_type import SessionType, db


class SessionTypeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SessionType
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    length = '00:30'
    event_id = 1
