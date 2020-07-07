from app.models.panel_permission import PanelPermission
from tests.factories import common
from tests.factories.base import BaseFactory


class PanelPermissionFactory(BaseFactory):
    class Meta:
        model = PanelPermission

    panel_name = common.string_
    can_access = True
