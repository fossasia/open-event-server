import factory
from app.models.ticket import db, TicketTag
from app.factories.ticket import TicketFactory
from app.factories.event import EventFactoryBasic
import app.factories.common as common


class TicketTagFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TicketTag
        sqlalchemy_session = db.session

    tickets = factory.RelatedFactory(TicketFactory)
    event = factory.RelatedFactory(EventFactoryBasic)
    name = common.string_
    event_id = 1
