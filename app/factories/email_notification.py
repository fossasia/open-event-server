import factory
from app.models.email_notification import db, EmailNotification
from app.factories.user import UserFactory
from app.factories.event import EventFactoryBasic


class EmailNotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = EmailNotification
        sqlalchemy_session = db.session

    user = factory.RelatedFactory(UserFactory)
    event = factory.RelatedFactory(EventFactoryBasic)
    next_event = 0
    new_paper = 0
    session_accept_reject = 0
    session_schedule = 1
    after_ticket_purchase = 1
    event_id = 1
    user_id = 2
