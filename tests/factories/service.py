import factory

import tests.factories.common as common
from app.models.service import Service, db


class ServiceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Service
        sqlalchemy_session = db.session

    name = common.string_
