import factory

import app.factories.common as common
from app.models.user_permission import db, UserPermission


class UserPermissionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = UserPermission
        sqlalchemy_session = db.session

    name = common.string_
    description = common.string_

    unverified_user = True
    anonymous_user = True
