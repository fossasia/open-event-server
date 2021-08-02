import factory

from app.models.export_job import ExportJob
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class ExportJobFactory(BaseFactory):
    class Meta:
        model = ExportJob

    task = common.string_
    user_email = common.string_
    event = factory.RelatedFactory(EventFactoryBasic)
