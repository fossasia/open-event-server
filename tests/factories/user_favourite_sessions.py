import factory

from app.models.session import Session
from app.models.user import User
from app.models.user_favourite_session import UserFavouriteSession
from tests.factories.base import BaseFactory


class UserFavouriteSessionFactory(BaseFactory):
    class Meta:
        model = UserFavouriteSession

    user = factory.LazyAttribute(lambda a: User.query.first())
    # session = factory.SubFactory(SessionFactory)
    session = factory.LazyAttribute(lambda a: Session.query.first())
