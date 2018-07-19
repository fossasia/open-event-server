import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.models.ticket_holder import db, TicketHolder


class AttendeeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TicketHolder
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
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
