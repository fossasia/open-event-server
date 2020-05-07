import factory

import tests.factories.common as common
from tests.factories.base import BaseFactory
from tests.factories.ticket import TicketFactory
from tests.factories.user import UserFactory
from app.models.discount_code import DiscountCode


class DiscountCodeFactory(BaseFactory):
    # class name to be DiscountCodeEventFactory?
    class Meta:
        model = DiscountCode

    marketer = factory.RelatedFactory(UserFactory)
    code = common.string_
    discount_url = common.url_
    value = common.float_
    type = "amount"
    is_active = True
    tickets_number = 30
    min_quantity = 10
    max_quantity = 20
    valid_from = common.date_
    valid_till = common.dateEnd_
    used_for = "event"
    marketer_id = 1
    event_id = None


class DiscountCodeTicketFactory(BaseFactory):
    class Meta:
        model = DiscountCode

    marketer = factory.RelatedFactory(UserFactory)
    tickets = factory.RelatedFactory(TicketFactory)
    code = common.string_
    discount_url = common.url_
    value = common.float_
    type = "amount"
    is_active = True
    tickets_number = 30
    min_quantity = 1
    max_quantity = 20
    valid_from = common.date_
    valid_till = common.dateEnd_
    used_for = "ticket"
    marketer_id = 1
    event_id = None
