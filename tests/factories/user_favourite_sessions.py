import factory

from app.models.user import User
from app.models.user_favourite_session import UserFavouriteSession
from tests.factories.base import BaseFactory
from tests.factories.session import SessionFactory


class UserFavouriteSessionFactory(BaseFactory):
    class Meta:
        model = UserFavouriteSession

    user = factory.LazyAttribute(lambda a: User.query.first())
    session = factory.SubFactory(SessionFactory)
