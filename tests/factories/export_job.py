import factory

import tests.factories.common as common
from tests.factories.event import EventFactoryBasic
from app.models.export_job import ExportJob, db


class ExportJobFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = ExportJob
        sqlalchemy_session = db.session

    task = common.string_
    user_email = common.string_
    event = factory.RelatedFactory(EventFactoryBasic)
