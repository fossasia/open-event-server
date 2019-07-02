import factory

from app.factories.session import SessionFactory
from app.factories.user import UserFactory
from app.models.feedback import db, Feedback


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
