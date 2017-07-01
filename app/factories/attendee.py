import factory
from app.models.ticket_holder import db, TicketHolder
import app.factories.common as common


class AttendeeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TicketHolder
        sqlalchemy_session = db.session

    firstname = common.string_
    lastname = common.string_
    email = common.email_
    address = common.string_
    city = common.string_
    state = common.string_
    country = "IN"
    is_checked_in = True
    pdf_url = common.url_
