import binascii
import os
import uuid

from app.models import db


class SoftDeletionModel(db.Model):
    """
        Base model for soft deletion support. All the models which support soft deletion should extend it.
    """

    __abstract__ = True

    deleted_at = db.Column(db.DateTime(timezone=True))

    def get_new_identifier(self):
        """
        Factory function that calls the model-appropriate method and returns an identifier
        :return:
        """
        model_name = type(self).__name__
        with db.session.no_autoflush:
            if model_name in {'Order', 'EventInvoice'}:
                identifier = self.random_uuid()
            elif model_name in {'SocialLink', 'Event'}:
                identifier = self.random_string_identifier()
            else:
                identifier = None
        return identifier

    def random_uuid(self):
        """
        Returns a random uuid (that's not already in use by the model that called this function) as a string, or calls itself again
        :return:
        """
        identifier = str(uuid.uuid4())
        if self.query.filter_by(identifier=identifier).first() is None:
            return identifier
        else:
            return self.random_uuid()

    def random_string_identifier(self, length=8):
        """
        Returns a random utf-8-encoded 8-character identifier that is not in use by the model that called this function
        :param length:
        :return:
        """
        identifier = str(binascii.b2a_hex(os.urandom(int(length / 2))), 'utf-8')
        if (
            not identifier.isdigit()
            and self.query.filter_by(identifier=identifier).first() is None
        ):
            return identifier
        else:
            return self.random_string_identifier(length)
