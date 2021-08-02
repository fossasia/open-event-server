import factory

from app.models.faq import Faq
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.faq_type import FaqTypeFactory


class FaqFactory(BaseFactory):
    class Meta:
        model = Faq

    event = factory.RelatedFactory(EventFactoryBasic)
    faq_type = factory.RelatedFactory(FaqTypeFactory)
    question = "Sample Question"
    answer = "Sample Answer"
    event_id = 1
    faq_type_id = 1
