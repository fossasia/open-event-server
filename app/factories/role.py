import factory

import app.factories.common as common
from app.models.role import db, Role
from app.models.user import ORGANIZER


class RoleFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Role
        sqlalchemy_session = db.session

    name = ORGANIZER
    title_name = common.string_
