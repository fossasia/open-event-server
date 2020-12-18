import factory

from app.models.ticket import TicketTag
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.ticket import TicketFactory


class TicketTagFactory(BaseFactory):
    class Meta:
        model = TicketTag

    tickets = factory.RelatedFactory(TicketFactory)
    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    event_id = 1
