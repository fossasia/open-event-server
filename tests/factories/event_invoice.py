import factory

from app.models.event_invoice import EventInvoice
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.user import UserFactory


class EventInvoiceFactoryBase(BaseFactory):
    class Meta:
        model = EventInvoice

    amount = common.float_
    transaction_id = common.string_
    paid_via = "stripe"
    payment_mode = common.string_
    brand = common.string_
    exp_month = "10"
    exp_year = "2100"
    last4 = "1234"
    stripe_token = common.string_
    paypal_token = common.string_


class EventInvoiceSubFactory(EventInvoiceFactoryBase):
    event = factory.SubFactory(EventFactoryBasic)


class EventInvoiceFactory(EventInvoiceFactoryBase):
    event = factory.RelatedFactory(EventFactoryBasic)
    user = factory.RelatedFactory(UserFactory)
    event_id = 1
    user_id = 2
