import factory

from app.models.access_code import AccessCode
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.ticket import TicketFactory
from tests.factories.user import UserFactory


class AccessCodeFactory(BaseFactory):
    class Meta:
        model = AccessCode

    tickets = factory.RelatedFactory(TicketFactory)
    user = factory.RelatedFactory(UserFactory)
    event = factory.RelatedFactory(EventFactoryBasic)
    code = common.string_
    access_url = common.url_
    is_active = True
    tickets_number = 30
    min_quantity = 10
    max_quantity = 20
    marketer_id = 1
    valid_from = common.date_
    valid_till = common.dateEnd_
    event_id = 1
