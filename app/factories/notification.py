import factory

import app.factories.common as common
from app.factories.user import UserFactory
from app.models.notification import db, Notification


class NotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Notification
        sqlalchemy_session = db.session

    user = factory.RelatedFactory(UserFactory)
    title = common.string_
    message = common.string_
    is_read = False
    user_id = 2
