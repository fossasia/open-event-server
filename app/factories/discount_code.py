import factory

import app.factories.common as common
from app.factories.user import UserFactory
from app.models.discount_code import db, DiscountCode


class DiscountCodeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DiscountCode
        sqlalchemy_session = db.session

    user = factory.RelatedFactory(UserFactory)
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
    tickets = "event"
    user_id = 1
    event_id = None
