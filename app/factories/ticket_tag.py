import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.factories.ticket import TicketFactory
from app.models.ticket import db, TicketTag


class TicketTagFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TicketTag
        sqlalchemy_session = db.session

    tickets = factory.RelatedFactory(TicketFactory)
    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    event_id = 1
