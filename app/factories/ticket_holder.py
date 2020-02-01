import factory

from app.factories.user import UserFactory
from app.factories.ticket import TicketFactory
from app.factories.order import OrderFactory, db
from app.models.ticket_holder import TicketHolder

class TicketHolderFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TicketHolder
        sqlalchemy_session = db.session

    ticket = factory.RelatedFactory(TicketFactory)
    user = factory.RelatedFactory(UserFactory)
    order = factory.RelatedFactory(OrderFactory)
    order_id = 1
