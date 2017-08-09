import factory
from app.models.mail import db, Mail
import app.factories.common as common


class MailFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Mail
        sqlalchemy_session = db.session

    recipient = common.email_
    time = common.date_
    action = common.string_
    subject = common.string_
    message = common.string_
