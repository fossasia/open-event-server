import factory

from app.models.role_invite import RoleInvite
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.role import RoleFactory


class RoleInviteFactoryBase(BaseFactory):
    class Meta:
        model = RoleInvite

    email = common.email_
    hash = common.secret_
    status = common.string_
    role_name = common.string_


class RoleInviteFactory(RoleInviteFactoryBase):

    event = factory.RelatedFactory(EventFactoryBasic)
    role = factory.RelatedFactory(RoleFactory)
    event_id = 1
    role_id = 1


class RoleInviteSubFactory(RoleInviteFactoryBase):

    event = factory.SubFactory(EventFactoryBasic)
    role = factory.SubFactory(RoleFactory)
