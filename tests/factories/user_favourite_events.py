import factory

from app.models.user import User
from app.models.user_favourite_event import UserFavouriteEvent
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class UserFavouriteEventFactory(BaseFactory):
    class Meta:
        model = UserFavouriteEvent

    user = factory.LazyAttribute(lambda a: User.query.first())
    event = factory.SubFactory(EventFactoryBasic)
