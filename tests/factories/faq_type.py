import factory

from app.models.faq_type import FaqType
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class FaqTypeFactory(BaseFactory):
    class Meta:
        model = FaqType

    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    event_id = 1
