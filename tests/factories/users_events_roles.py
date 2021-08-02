import factory

from app.models.users_events_role import UsersEventsRoles
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.role import RoleFactory
from tests.factories.user import UserFactory


class UsersEventsRolesFactoryBasic(BaseFactory):
    class Meta:
        model = UsersEventsRoles


class UsersEventsRolesFactory(UsersEventsRolesFactoryBasic):
    class Meta:
        model = UsersEventsRoles

    event = factory.RelatedFactory(EventFactoryBasic)
    role = factory.RelatedFactory(RoleFactory)
    user = factory.RelatedFactory(UserFactory)
    event_id = 1
    role_id = 1
    user_id = 1


class UsersEventsRolesSubFactory(UsersEventsRolesFactoryBasic):
    user = factory.SubFactory(UserFactory)
    event = factory.SubFactory(EventFactoryBasic)
    role = factory.SubFactory(RoleFactory)
