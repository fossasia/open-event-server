import factory

from app.models.ticket_holder import TicketHolder
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.order import OrderFactory, OrderSubFactory
from tests.factories.ticket import TicketFactory, TicketSubFactory


class AttendeeFactoryBase(BaseFactory):
    class Meta:
        model = TicketHolder

    firstname = common.string_
    lastname = common.string_
    email = common.email_
    address = common.string_
    city = common.string_
    state = common.string_
    country = "IN"
    is_checked_in = True
    pdf_url = common.url_
    ticket_id = None
    order_id = None
    modified_at = common.date_


class AttendeeSubFactory(AttendeeFactoryBase):
    event = factory.SubFactory(EventFactoryBasic)
    ticket = factory.SubFactory(TicketSubFactory)


class AttendeeOrderSubFactory(AttendeeSubFactory):
    order = factory.SubFactory(OrderSubFactory)


class AttendeeOrderTicketSubFactory(AttendeeOrderSubFactory):
    pass


class AttendeeFactory(AttendeeFactoryBase):
    event = factory.RelatedFactory(EventFactoryBasic)
    ticket = factory.RelatedFactory(TicketFactory)
    order = factory.RelatedFactory(OrderFactory)
    event_id = 1
    ticket_id = 1
