from app.models.mail import Mail
from tests.factories import common
from tests.factories.base import BaseFactory


class MailFactory(BaseFactory):
    class Meta:
        model = Mail

    recipient = common.email_
    time = common.date_
    action = common.string_
    subject = common.string_
    message = common.string_
