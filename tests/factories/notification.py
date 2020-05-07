import factory

import tests.factories.common as common
from app.models.notification import Notification
from tests.factories.base import BaseFactory
from tests.factories.user import UserFactory


class NotificationFactory(BaseFactory):
    class Meta:
        model = Notification

    user = factory.RelatedFactory(UserFactory)
    title = common.string_
    message = common.string_
    is_read = False
    user_id = 2
