import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.factories.ticket import TicketFactory
from app.factories.order import OrderFactory
from app.models.ticket_holder import db, TicketHolder


class AttendeeFactoryBase(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TicketHolder
        sqlalchemy_session = db.session

    firstname = common.string_
    lastname = common.string_
    email = common.email_
    address = common.string_
    city = common.string_
    state = common.string_
    country = "IN"
    is_checked_in = True
    pdf_url = common.url_
    event_id = 1
    ticket_id = None
    order_id = None
    created_at = common.date_
    modified_at = common.date_


class AttendeeFactory(AttendeeFactoryBase):
    event = factory.RelatedFactory(EventFactoryBasic)
    ticket = factory.RelatedFactory(TicketFactory)
    order = factory.RelatedFactory(OrderFactory)
