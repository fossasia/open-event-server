import factory

import app.factories.common as common
from app.models.mail import db, Mail


class MailFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Mail
        sqlalchemy_session = db.session

    recipient = common.email_
    time = common.date_
    action = common.string_
    subject = common.string_
    message = common.string_
