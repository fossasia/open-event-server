import factory
from app.models.user_permission import db, UserPermission
import app.factories.common as common


class UserPermissionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = UserPermission
        sqlalchemy_session = db.session

    name = common.string_
    description = common.string_

    unverified_user = True
    anonymous_user = True
