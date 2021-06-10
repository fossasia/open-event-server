import factory

from app.models.ticket import Ticket
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class TicketFactoryBase(BaseFactory):
    class Meta:
        model = Ticket

    name = common.string_
    description = common.string_
    type = common.string_
    price = common.float_
    quantity = 10
    is_description_visible = True
    position = 10
    is_fee_absorbed = True
    sales_starts_at = common.date_
    sales_ends_at = common.dateEnd_
    is_hidden = True
    min_order = 0
    max_order = 10


class TicketFactory(TicketFactoryBase):
    event = factory.RelatedFactory(EventFactoryBasic)
    event_id = 1


class TicketSubFactory(TicketFactoryBase):
    event = factory.SubFactory(EventFactoryBasic)
