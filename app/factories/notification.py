import factory
from app.models.notification import db, Notification
from app.factories.user import UserFactory
import app.factories.common as common


class NotificationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Notification
        sqlalchemy_session = db.session

    user = factory.RelatedFactory(UserFactory)
    title = common.string_
    message = common.string_
    action = common.string_
    is_read = False
    user_id = 2

