import factory

import tests.factories.common as common
from app.models.role_invite import RoleInvite
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.role import RoleFactory


class RoleInviteFactory(BaseFactory):
    class Meta:
        model = RoleInvite

    event = factory.RelatedFactory(EventFactoryBasic)
    role = factory.RelatedFactory(RoleFactory)
    email = common.email_
    hash = common.string_
    status = common.string_
    role_name = common.string_
    event_id = 1
    role_id = 1
