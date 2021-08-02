from sqlalchemy.ext.hybrid import hybrid_property

from app.api.helpers.db import get_or_create
from app.api.helpers.system_mails import MAILS, MailType
from app.models import db
from app.models.helpers.timestamp import Timestamp


class MessageSettings(db.Model, Timestamp):
    "Used for emails"

    __tablename__ = 'message_settings'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String, nullable=False)
    enabled = db.Column(db.Boolean, default=True, nullable=False, server_default='True')

    def __repr__(self):
        return '<Message Setting %r >' % self.action

    @staticmethod
    def is_enabled(action: str) -> bool:
        settings, _ = get_or_create(
            MessageSettings, action=action, defaults=dict(enabled=True)
        )

        return settings.enabled

    @classmethod
    def _email_message(cls, action, attr=None):
        message = {}
        if action in MailType.entries():
            message = MAILS.get(action)
        else:
            message = MAILS.__dict__[action]
        fallback_message = 'Dynamic Mail'
        if not message:
            return fallback_message
        if attr == 'message' and (template := message.get('template')):
            return open('app/templates/' + template).read()
        message = str(message.get(attr) or fallback_message)
        return message

    @hybrid_property
    def email_message(self):
        message = self._email_message(self.action, attr='message')
        return message

    @hybrid_property
    def recipient(self):
        message = self._email_message(self.action, attr='recipient')
        return message

    @hybrid_property
    def email_subject(self):
        message = self._email_message(self.action, attr='subject')
        return message
