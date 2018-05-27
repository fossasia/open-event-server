import factory

import app.factories.common as common
from app.models.service import db, Service


class ServiceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Service
        sqlalchemy_session = db.session

    name = common.string_
