import tests.factories.common as common
from app.models.role import Role
from app.models.user import ORGANIZER
from tests.factories.base import BaseFactory


class RoleFactory(BaseFactory):
    class Meta:
        model = Role

    name = ORGANIZER
    title_name = common.string_
