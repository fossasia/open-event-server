import factory

from app.models.tax import Tax
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class TaxFactoryBase(BaseFactory):
    class Meta:
        model = Tax

    country = common.country_
    name = common.string_
    rate = common.float_
    tax_id = "123456789"
    should_send_invoice = False
    registered_company = common.string_
    address = common.string_
    city = common.string_
    state = common.string_
    zip = "123456"
    invoice_footer = common.string_
    is_tax_included_in_price = False


class TaxFactory(TaxFactoryBase):
    event = factory.RelatedFactory(EventFactoryBasic)
    event_id = 1


class TaxSubFactory(TaxFactoryBase):
    event = factory.SubFactory(EventFactoryBasic)
