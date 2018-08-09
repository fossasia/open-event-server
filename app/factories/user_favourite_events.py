import factory

from app.factories.event import EventFactoryBasic
from app.factories.user import UserFactory
from app.models.user_favourite_event import UserFavouriteEvent
from app.models import db


class UserFavouriteEventFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = UserFavouriteEvent
        sqlalchemy_session = db.session

    user = factory.RelatedFactory(UserFactory)
    event = factory.RelatedFactory(EventFactoryBasic)
