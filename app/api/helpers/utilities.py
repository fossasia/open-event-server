# PLEASE PUT ALL FUNCTIONS WHICH PERFORM GENERAL FORMATTING ON ANY DATATYPE WITHOUT USING ANY
# MODULES RELATED TO THE EVENT-SYSTEM i.e FUNCTIONS SPECIFIC TO DB MODELS E.G A FUNCTION JUST FOR ROLE_INVITES
import random
import re
import string
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, List, Optional, Tuple

import bleach
import requests
from flask import current_app
from itsdangerous import Serializer

from app.api.helpers.errors import UnprocessableEntityError


def make_dict(list_of_object, key) -> dict:
    """
    To convert a list of object into dict.

    This will return a dict containing unique keys
    mapped to the object which contains that key.
    """
    mapped_dict = {}
    for obj in list_of_object:
        mapped_dict[getattr(obj, key)] = obj
    return mapped_dict


def dasherize(text: str) -> str:
    return text.replace('_', '-')


def to_snake_case(text: str) -> str:
    text = text.replace('-', '_')
    return re.sub('([A-Z]+)', r'_\1', text).lower()


def dict_to_snake_case(input_dict: Dict[str, Any]) -> Dict[str, Any]:
    if not input_dict:
        return input_dict

    output = {}
    for key, val in input_dict.items():
        output[to_snake_case(key)] = val

    return output


def require_relationship(resource_list: List[Any], data: Dict[Any]) -> None:
    for resource in resource_list:
        if resource not in data:
            raise UnprocessableEntityError(
                {'pointer': f'/data/relationships/{resource}'},
                f"A valid relationship with {resource} resource is required",
            )


def string_empty(value) -> bool:
    return isinstance(value, str) and not value.strip()


def strip_tags(html) -> Optional[str]:
    if html is None:
        return None
    return bleach.clean(html, tags=[], attributes={}, styles=[], strip=True)


def get_serializer(secret_key='secret_key') -> Serializer:
    return Serializer(secret_key)


def str_generator(size=6, chars=string.ascii_uppercase + string.digits) -> str:
    return ''.join(random.choice(chars) for _ in range(size))


# From http://stackoverflow.com/a/3425124
def monthdelta(date: datetime, delta: int) -> datetime:
    m, y = (date.month + delta) % 12, date.year + (date.month + delta - 1) // 12
    if not m:
        m = 12
    d = min(
        date.day,
        [
            31,
            29 if y % 4 == 0 and not y % 400 == 0 else 28,
            31,
            30,
            31,
            30,
            31,
            31,
            30,
            31,
            30,
            31,
        ][m - 1],
    )
    return date.replace(day=d, month=m, year=y)


def represents_int(value) -> bool:
    try:
        int(value)
        return True
    except:
        return False


def is_downloadable(url: str) -> bool:
    """
    Does the url contain a downloadable resource
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    # content_length = header.get('content-length', 1e10)
    if content_type and 'text' in content_type.lower():
        return False
    if content_type and 'html' in content_type.lower():
        return False
    return True


def get_filename_from_cd(cd: str) -> Tuple[Any, str]:
    """
    Get filename and ext from content-disposition
    """
    if not cd:
        return '', ''
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return '', ''
    fn = fname[0].rsplit('.', 1)
    return fn[0], '' if len(fn) == 1 else ('.' + fn[1])


def write_file(file, data) -> None:
    """simple write to file"""
    fp = open(file, 'w')
    fp.write(str(data, 'utf-8'))
    fp.close()


def update_state(task_handle, state, result=None) -> None:
    """
    Update state of celery task
    """
    if result is None:
        result = {}
    if not current_app.config.get('CELERY_ALWAYS_EAGER'):
        task_handle.update_state(state=state, meta=result)


def round_money(money) -> Decimal:
    return Decimal(money).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


static_page = 'https://eventyay.com/'
image_link = 'https://www.gstatic.com/webp/gallery/1.jpg'

# store task results in case of testing
# state and info
TASK_RESULTS = {}


class EmptyObject:
    pass
