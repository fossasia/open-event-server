import factory

from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from app.models.order import Order


class OrderFactory(BaseFactory):
    class Meta:
        model = Order

    event = factory.RelatedFactory(EventFactoryBasic)
    event_id = 1
    payment_mode = 'free'
    status = 'initializing'
