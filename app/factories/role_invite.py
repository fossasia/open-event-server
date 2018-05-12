import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.factories.role import RoleFactory
from app.models.role_invite import db, RoleInvite


class RoleInviteFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = RoleInvite
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    role = factory.RelatedFactory(RoleFactory)
    email = common.email_
    created_at = common.date_
    hash = common.string_
    status = common.string_
    role_name = common.string_
    event_id = 1
    role_id = 1
