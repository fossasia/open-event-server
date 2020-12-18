import factory

from app.models.discount_code import DiscountCode
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.ticket import TicketFactory
from tests.factories.user import UserFactory


class DiscountCodeFactory(BaseFactory):
    # class name to be DiscountCodeEventFactory?
    class Meta:
        model = DiscountCode

    marketer = factory.RelatedFactory(UserFactory)
    code = factory.Sequence(lambda n: 'john%s' % n)
    discount_url = common.url_
    value = common.float_
    type = "amount"
    is_active = True
    tickets_number = 30
    min_quantity = 1
    max_quantity = 20
    valid_from = common.date_
    valid_till = common.dateEnd_
    used_for = "event"
    marketer_id = 1
    event_id = None


class DiscountCodeTicketFactoryBase(BaseFactory):
    class Meta:
        model = DiscountCode

    code = common.string_
    discount_url = common.url_
    value = common.float_
    type = "amount"
    is_active = True
    tickets_number = 30
    min_quantity = 0
    max_quantity = 20
    valid_from = common.date_
    valid_till = common.dateEnd_
    used_for = "ticket"


class DiscountCodeTicketSubFactory(DiscountCodeTicketFactoryBase):
    tickets = factory.SubFactory(TicketFactory)


class DiscountCodeTicketFactory(DiscountCodeTicketFactoryBase):
    marketer = factory.RelatedFactory(UserFactory)
    tickets = factory.RelatedFactory(TicketFactory)
    marketer_id = 1
    event_id = None
