import factory

from app.factories.role import RoleFactory
from app.factories.service import ServiceFactory
from app.models.permission import db, Permission


class EventRolePermissionsFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Permission
        sqlalchemy_session = db.session

    role = factory.RelatedFactory(RoleFactory)
    service = factory.RelatedFactory(ServiceFactory)
    can_create = True
    can_read = True
    can_update = True
    can_delete = True
    role_id = 1
    service_id = 1
