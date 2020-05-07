import factory

from app.models.permission import Permission
from tests.factories.base import BaseFactory
from tests.factories.role import RoleFactory
from tests.factories.service import ServiceFactory


class EventRolePermissionsFactory(BaseFactory):
    class Meta:
        model = Permission

    role = factory.RelatedFactory(RoleFactory)
    service = factory.RelatedFactory(ServiceFactory)
    can_create = True
    can_read = True
    can_update = True
    can_delete = True
    role_id = 1
    service_id = 1
