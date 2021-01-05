from app.models.role import Role
from tests.factories import common
from tests.factories.base import BaseFactory


class RoleFactory(BaseFactory):
    class Meta:
        model = Role

    name = Role.ORGANIZER
    title_name = common.string_
