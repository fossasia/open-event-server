import factory

import tests.factories.common as common
from tests.factories.event import EventFactoryBasic
from tests.factories.ticket import TicketFactory
from app.models.ticket import TicketTag, db


class TicketTagFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TicketTag
        sqlalchemy_session = db.session

    tickets = factory.RelatedFactory(TicketFactory)
    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    event_id = 1
