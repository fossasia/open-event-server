import factory

from app.models.notification import Notification, NotificationActor, NotificationContent
from tests.factories import common
from tests.factories.base import BaseFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.user import UserFactory


class NotificationFactoryBase(BaseFactory):
    class Meta:
        model = Notification

    is_read = False


class NotificationContentSubFactory(BaseFactory):
    class Meta:
        model = NotificationContent

    type = common.string_
    target = factory.SubFactory(EventFactoryBasic)


class NotificationActorSubFactory(BaseFactory):
    class Meta:
        model = NotificationActor

    actor = factory.SubFactory(UserFactory)
    content = factory.SubFactory(NotificationContentSubFactory)


class NotificationSubFactory(NotificationFactoryBase):

    user = factory.SubFactory(UserFactory)
    content = factory.SubFactory(NotificationContentSubFactory)
