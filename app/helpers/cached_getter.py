from app.helpers.cache import cache
from app.models.ticket import Ticket
from app.models.discount_code import DiscountCode
from app.models.user import User

from app.helpers.data_getter import DataGetter

class CachedGetter(object):
    """Cached data getters"""

    @staticmethod
    @cache.memoize(50)
    def get_ticket(ticket_id):
        return Ticket.query.get(ticket_id)

    @staticmethod
    @cache.memoize(50)
    def get_event(event_id):
        return DataGetter.get_event(event_id, False)

    @staticmethod
    @cache.memoize(50)
    def get_discount_code(discount_code_id):
        return DiscountCode.query.get(discount_code_id)

    @staticmethod
    @cache.memoize(50)
    def get_user(user_id):
        return User.query.get(user_id)
