import factory
import app.factories.common as common

from app.factories.event import EventFactoryBasic
from app.factories.user import UserFactory
from app.models.order import Order
from app.models.ticket import db


class OrderFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Order
        sqlalchemy_session = db.session

    user = factory.RelatedFactory(UserFactory)
    event = factory.RelatedFactory(EventFactoryBasic)
    event_id = 1
    payment_mode = 'free'
    status = 'initializing'
