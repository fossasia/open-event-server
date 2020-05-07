import tests.factories.common as common
from app.models.custom_system_role import CustomSysRole
from tests.factories.base import BaseFactory


class CustomSysRoleFactory(BaseFactory):
    class Meta:
        model = CustomSysRole

    name = common.string_
