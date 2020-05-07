import factory

import tests.factories.common as common
from tests.factories.user import UserFactory
from app.models.notification import Notification, db


class NotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Notification
        sqlalchemy_session = db.session

    user = factory.RelatedFactory(UserFactory)
    title = common.string_
    message = common.string_
    is_read = False
    user_id = 2
