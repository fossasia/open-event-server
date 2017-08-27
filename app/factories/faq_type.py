import factory
from app.models.faq_type import db, FaqType
from app.factories.event import EventFactoryBasic
import app.factories.common as common


class FaqTypeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = FaqType
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    event_id = 1
