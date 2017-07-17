import factory
from app.models.email_notification import db, EmailNotification
from app.factories.user import UserFactory
import app.factories.common as common


class EmailNotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = EmailNotification
        sqlalchemy_session = db.session

    user = factory.RelatedFactory(UserFactory)
    next_event = 0
    new_paper = 0
    session_accept_reject = 0
    session_schedule = 1
    after_ticket_purchase = 1
