import factory

from tests.factories.event import EventFactoryBasic
from tests.factories.faq_type import FaqTypeFactory
from app.models.faq import Faq, db


class FaqFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Faq
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    faq_type = factory.RelatedFactory(FaqTypeFactory)
    question = "Sample Question"
    answer = "Sample Answer"
    event_id = 1
    faq_type_id = 1
