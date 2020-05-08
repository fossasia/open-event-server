import factory

from app.models import db
from objproxies import CallbackProxy


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session = CallbackProxy(lambda: db.session)
