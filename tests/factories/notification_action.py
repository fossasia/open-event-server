from app.models import notification as notification
from tests.factories import common as common
from tests.factories.base import BaseFactory


class NotificationActionFactory(BaseFactory):
    class Meta:
        model = notification.NotificationAction

    subject = ('event',)
    link = (common.url_,)
    subject_id = (1,)
    action_type = 'view'
