import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.models.ticket import db, Ticket


class TicketFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Ticket
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
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
    event_id = 1
