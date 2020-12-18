import factory
from objproxies import CallbackProxy

from app.models import db


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = CallbackProxy(lambda: db.session)
