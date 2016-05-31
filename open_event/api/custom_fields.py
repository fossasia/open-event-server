import re
from flask.ext.restplus.fields import Raw
import colour


EMAIL_REGEX = re.compile(r'\S+@\S+\.\S+')
URI_REGEX = re.compile(r'(http|https|ftp)://\S+\.\S+')


class CustomField(Raw):
    """
    Custom Field base class with validate feature
    """
    def format(self, value):
        """
        format the text in database for output
        works only for GET requests
        """
        if not self.validate(value):
            print 'Validation of field with value \"%s\" (%s) failed' % (
                value, str(self.__class__.__name__))
            # raise MarshallingError
            # disabling for development purposes as the server crashes when
            # exception is raised. can be enabled when the project is mature
        if self.__schema_type__ == 'string':
            return unicode(value)
        else:
            return value

    def validate(self, value):
        """
        Validate the value. return True if valid
        """
        return True


class EmailField(CustomField):
    """
    Email field
    """
    __schema_type__ = 'string'
    __schema_format__ = 'email'
    __schema_example__ = 'email@domain.com'

    def validate(self, value):
        if not self.required and not value:
            return True
        if not EMAIL_REGEX.match(value):
            return False
        return True


class UriField(CustomField):
    """
    URI (link) field
    """
    __schema_type__ = 'string'
    __schema_format__ = 'uri'
    __schema_example__ = 'http://website.com'

    def validate(self, value):
        if not self.required and not value:
            return True
        if not URI_REGEX.match(value):
            return False
        return True


class ImageUriField(CustomField):
    """
    Image URL (url ends with image.ext) field
    """
    __schema_example__ = 'http://website.com/image.ext'


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
