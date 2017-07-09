import factory
from app.models.users_events_role import db, UsersEventsRoles
from app.factories.event import EventFactoryBasic
import app.factories.common as common


class UsersEventsRoleFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = UsersEventsRoles
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
