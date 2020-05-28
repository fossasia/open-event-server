import factory

from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from app.models.order import Order


class OrderFactoryBase(BaseFactory):
    class Meta:
        model = Order

    payment_mode = 'free'
    status = 'initializing'


class OrderSubFactory(OrderFactoryBase):
    event = factory.SubFactory(EventFactoryBasic)


class OrderFactory(OrderFactoryBase):
    event = factory.RelatedFactory(EventFactoryBasic)
    event_id = 1
