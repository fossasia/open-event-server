import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.factories.ticket import TicketFactory
from app.factories.user import UserFactory
from app.models.access_code import db, AccessCode


class AccessCodeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AccessCode
        sqlalchemy_session = db.session

    tickets = factory.RelatedFactory(TicketFactory)
    user = factory.RelatedFactory(UserFactory)
    event = factory.RelatedFactory(EventFactoryBasic)
    code = common.string_
    access_url = common.url_
    is_active = True
    tickets_number = 10
    min_quantity = 10
    max_quantity = 100
    valid_from = common.date_
    valid_till = common.dateEnd_
    used_for = common.string_
    user_id = 1
    event_id = 1
