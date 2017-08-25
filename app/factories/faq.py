import factory
from app.models.faq import db, Faq
from app.factories.event import EventFactoryBasic


class FaqFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:
        model = Faq
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    question = "Sample Question"
    answer = "Sample Answer"
    event_id = 1
