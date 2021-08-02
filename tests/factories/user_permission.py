from app.models.user_permission import UserPermission
from tests.factories import common
from tests.factories.base import BaseFactory


class UserPermissionFactory(BaseFactory):
    class Meta:
        model = UserPermission

    name = common.string_
    description = common.string_

    unverified_user = True
    anonymous_user = True
