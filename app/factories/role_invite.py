import factory
from app.models.role_invite import db, RoleInvite
from app.factories.event import EventFactoryBasic
import app.factories.common as common


class RoleInviteFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = RoleInvite
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    email = common.email_
    hash = common.string_
    created_at = common.date_
    role_id = common.int_
    is_declined = False
