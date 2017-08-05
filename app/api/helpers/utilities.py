# PLEASE PUT ALL FUNCTIONS WHICH PERFORM GENERAL FORMATTING ON ANY DATATYPE WITHOUT USING ANY
# MODULES RELATED TO THE EVENT-SYSTEM i.e FUNCTIONS SPECIFIC TO DB MODELS E.G A FUNCTION JUST FOR ROLE_INVITES
import random
import string

import bleach
from itsdangerous import Serializer

from app.api.helpers.exceptions import UnprocessableEntity



def dasherize(text):
    return text.replace('_', '-')


def require_relationship(resource_list, data):
    for resource in resource_list:
        if resource not in data:
            raise UnprocessableEntity({'pointer': '/data/relationships/{}'.format(resource)},
                                      "A valid relationship with {} resource is required".format(resource))


def string_empty(value):
    if type(value) is not value and type(value) is not unicode:
        return False
    if value and value.strip() and value != u'' and value != u' ':
        return False
    else:
        return True


def strip_tags(html):
    return bleach.clean(html, tags=[], attributes={}, styles=[], strip=True)


def get_serializer(secret_key='secret_key'):
    return Serializer(secret_key)


def str_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


# From http://stackoverflow.com/a/3425124
def monthdelta(date, delta):
    m, y = (date.month + delta) % 12, date.year + (date.month + delta - 1) // 12
    if not m:
        m = 12
    d = min(date.day, [31,
                       29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return date.replace(day=d, month=m, year=y)


def represents_int(value):
    try:
        int(value)
        return True
    except:
        return False
