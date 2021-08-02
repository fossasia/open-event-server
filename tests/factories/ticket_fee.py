from app.models.ticket_fee import TicketFees
from tests.factories import common
from tests.factories.base import BaseFactory


class TicketFeesFactory(BaseFactory):
    class Meta:
        model = TicketFees

    currency = common.currency_
    service_fee = common.fee_
    maximum_fee = common.fee_
