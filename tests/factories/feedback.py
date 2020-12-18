import factory

from app.models.feedback import Feedback
from tests.factories.base import BaseFactory
from tests.factories.session import SessionFactory
from tests.factories.user import UserFactory


class FeedbackFactory(BaseFactory):
    class Meta:
        model = Feedback

    session = factory.RelatedFactory(SessionFactory)
    user = factory.RelatedFactory(UserFactory)
    rating = "4"
    comment = "Awesome session."
    session_id = 1
    user_id = 1
