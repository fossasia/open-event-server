import factory

from app.factories.event import EventFactoryBasic
from app.factories.user import UserFactory
from app.models.feedback import db, Feedback


class FeedbackFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:
        model = Feedback
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    user = factory.RelatedFactory(UserFactory)
    rating = "4"
    comment = "Awesome event."
    event_id = 1
    user_id = 2
