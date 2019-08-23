import factory

from app.factories.user import UserFactory
from app.factories.event import EventFactoryBasic
from app.models.users_events_role import db, UsersEventsRoles


class UsersEventsRoleFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = UsersEventsRoles
        sqlalchemy_session = db.session

    user = factory.RelatedFactory(UserFactory)
    user_id = 1
    event = factory.RelatedFactory(EventFactoryBasic)
