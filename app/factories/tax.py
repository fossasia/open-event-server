import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.models.tax import db, Tax


class TaxFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Tax
        sqlalchemy_session = db.session

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
