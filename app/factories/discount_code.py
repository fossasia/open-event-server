import factory
from app.models.discount_code import db, DiscountCode
from app.factories.event import EventFactoryBasic
import app.factories.common as common


class DiscountCodeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = DiscountCode
        sqlalchemy_session = db.session

    event = factory.RelatedFactory(EventFactoryBasic)
    code = common.string_
    discount_url = common.url_
    value = common.float_
    type = "amount"
    is_active = True
    tickets_number = 10
    min_quantity = 10
    max_quantity = 10
    valid_from = common.date_
    valid_till = common.dateEnd_
    used_for = common.string_
    tickets = "event"
