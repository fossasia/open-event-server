import factory

from app.factories.user import UserFactory
from app.factories.event import EventFactoryBasic
from app.models.user_favourite_event import db, UserFavouriteEvent
from app.models.user import User


class UserFavouriteEventFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = UserFavouriteEvent
        sqlalchemy_session = db.session

    user = factory.LazyAttribute(lambda a: User.query.first())
    event = factory.SubFactory(EventFactoryBasic)
