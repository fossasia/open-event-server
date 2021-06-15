import factory

from app.models.order import Order
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class OrderFactoryBase(BaseFactory):
    class Meta:
        model = Order

    payment_mode = 'free'
    status = 'initializing'
    tax_business_info = 'tax id'
    company = 'company'


class OrderSubFactory(OrderFactoryBase):
    event = factory.SubFactory(EventFactoryBasic)


class OrderFactory(OrderFactoryBase):
    event = factory.RelatedFactory(EventFactoryBasic)
    event_id = 1
