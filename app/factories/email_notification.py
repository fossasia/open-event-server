import factory

from app.factories.event import EventFactoryBasic
from app.factories.user import UserFactory
from app.models.email_notification import db, EmailNotification


class EmailNotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = EmailNotification
        sqlalchemy_session = db.session

    user = factory.RelatedFactory(UserFactory)
    event = factory.RelatedFactory(EventFactoryBasic)
    next_event = False
    new_paper = False
    session_accept_reject = False
    session_schedule = True
    after_ticket_purchase = True
    event_id = 1
    user_id = 2
