import factory

from app.models.email_notification import EmailNotification
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.user import UserFactory


class EmailNotificationFactory(BaseFactory):
    class Meta:
        model = EmailNotification

    user = factory.RelatedFactory(UserFactory)
    event = factory.RelatedFactory(EventFactoryBasic)
    next_event = False
    new_paper = False
    session_accept_reject = False
    session_schedule = True
    after_ticket_purchase = True
    event_id = 1
    user_id = 2
