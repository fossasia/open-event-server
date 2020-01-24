import factory

from app.models.module import Module, db


class ModuleFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:
        model = Module
        sqlalchemy_session = db.session

    donation_include = True
    ticket_include = True
    payment_include = True
