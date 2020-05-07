from app.models.message_setting import MessageSettings
from tests.factories.base import BaseFactory


class MessageSettingsFactory(BaseFactory):
    class Meta:
        model = MessageSettings

    action = "After Event"
    mail_status = True
    notification_status = True
    user_control_status = True
