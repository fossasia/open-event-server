import factory

from tests.factories.session import SessionFactory
from tests.factories.user import UserFactory
from app.models.feedback import Feedback, db


class FeedbackFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Feedback
        sqlalchemy_session = db.session

    session = factory.RelatedFactory(SessionFactory)
    user = factory.RelatedFactory(UserFactory)
    rating = "4"
    comment = "Awesome session."
    session_id = 1
    user_id = 1
