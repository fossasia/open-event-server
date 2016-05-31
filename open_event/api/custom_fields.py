import re
from flask.ext.restplus.fields import Raw, MarshallingError
import colour


EMAIL_REGEX = re.compile(r'\S+@\S+\.\S+')
URI_REGEX = re.compile(r'(http|https|ftp)://\S+\.\S+')


class CustomField(Raw):
    """
    Custom Field base class with validate feature
    """
    def format(self, value):
        if not self.validate(value):
            raise MarshallingError
        return value

    def validate(self, value):
        """
        Validate the value. return True if valid
        """
        return True


class EmailField(CustomField):
    """
    Custom email field
    """
    __schema_type__ = 'string'
    __schema_format__ = 'email'
    __schema_example__ = 'email@gmail.com'

    def validate(self, value):
        if not self.required and not value:
            return True
        if not EMAIL_REGEX.match(value):
            return False
        return True


class UriField(CustomField):
    """
    Custom URI (link) field
    """
    __schema_type__ = 'string'
    __schema_format__ = 'uri'
    __schema_example__ = 'http://example.com'

    def validate(self, value):
        if not self.required and not value:
            return True
        if not URI_REGEX.match(value):
            return False
        return True


class ColorField(CustomField):
    """
    Color (or colour) field
    """
    __schema_type__ = 'string'
    __schema_format__ = 'color'
    __schema_example__ = 'green'

    def validate(self, value):
        if not self.required and not value:
            return True
        try:
            # using the same colour package used by sqlalchemy and wtforms
            colour.Color(value)
        except Exception:
            return False
        return True
