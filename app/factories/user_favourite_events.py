import factory

from app.factories.event import EventFactoryBasic
from app.factories.user import UserFactory
from app.models.user import User
from app.models.user_favourite_event import UserFavouriteEvent, db


class UserFavouriteEventFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = UserFavouriteEvent
        sqlalchemy_session = db.session

    user = factory.LazyAttribute(lambda a: User.query.first())
    event = factory.SubFactory(EventFactoryBasic)
