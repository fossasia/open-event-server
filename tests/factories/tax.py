import factory

import tests.factories.common as common
from app.models.tax import Tax
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic


class TaxFactory(BaseFactory):
    class Meta:
        model = Tax

    event = factory.RelatedFactory(EventFactoryBasic)
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
    event_id = 1
