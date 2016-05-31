import re
from flask.ext.restplus.fields import Raw, MarshallingError


EMAIL_REGEX = re.compile(r'\S+@\S+\.\S+')


class EmailField(Raw):
    """
    Custom email field
    """
    __schema_type__ = 'string'
    __schema_format__ = 'email'
    __schema_example__ = 'email@gmail.com'

    def format(self, value):
        print self.required
        if not EMAIL_REGEX.match(value):
            raise MarshallingError
        return value


class UriField(Raw):
    """
    Custom URI (link) field
    """
    __schema_type__ = 'string'
    __schema_format__ = 'uri'
    __schema_example__ = 'http://example.com'

    def format(self, value):
        if value == 'abc':
            raise MarshallingError
        return value
