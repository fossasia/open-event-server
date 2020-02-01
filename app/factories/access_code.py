import factory

import app.factories.common as common
from app.factories.event import EventFactoryBasic
from app.factories.ticket import TicketFactory
from app.factories.user import UserFactory
from app.models.access_code import AccessCode, db


class AccessCodeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AccessCode
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = 'commit'

    tickets = factory.RelatedFactory(TicketFactory)
    user = factory.RelatedFactory(UserFactory)
    event = factory.RelatedFactory(EventFactoryBasic)
    code = common.string_
    access_url = common.url_
    is_active = True
    tickets_number = 30
    min_quantity = 10
    max_quantity = 20
    valid_from = common.date_
    valid_till = common.dateEnd_
