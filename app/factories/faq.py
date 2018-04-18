import factory

from app.factories.event import EventFactoryBasic
from app.factories.faq_type import FaqTypeFactory
from app.models.faq import db, Faq


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
