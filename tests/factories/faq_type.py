import factory

import tests.factories.common as common
from tests.factories.event import EventFactoryBasic
from app.models.faq_type import FaqType, db


class FaqTypeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = FaqType
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    event_id = 1
