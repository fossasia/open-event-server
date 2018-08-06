import factory

import app.factories.common as common
import app.models.notification as notification
from app.models import db


class NotificationActionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = notification.NotificationAction
        sqlalchemy_session = db.session

    subject = 'event',
    link = common.url_,
    subject_id = 1,
    action_type = 'view'
