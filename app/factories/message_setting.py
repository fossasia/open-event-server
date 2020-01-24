import factory

from app.models.message_setting import MessageSettings, db


class MessageSettingsFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = MessageSettings
        sqlalchemy_session = db.session

    action = "After Event"
    mail_status = True
    notification_status = True
    user_control_status = True
