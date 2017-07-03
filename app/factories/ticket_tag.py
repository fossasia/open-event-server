import factory
from app.models.ticket import db, TicketTag, ticket_tags_table
from app.factories.ticket import TicketFactory
import app.factories.common as common


class TicketTagFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TicketTag
        sqlalchemy_session = db.session

    ticket = factory.RelatedFactory(TicketFactory)
    name = common.string_
